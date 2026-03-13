#!/usr/bin/env python3
"""
案件応募自動化システム - Google Sheets 同期スクリプト
役割: inbox/ の jsonl を読み取り、Google Sheets に反映する
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---- パス設定 ----
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "inbox"
PROCESSED_DIR = BASE_DIR / "processed"
ERROR_DIR = BASE_DIR / "error"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_PATH = BASE_DIR / "config.json"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ---- 必須フィールド定義 ----
REQUIRED_FIELDS = {
    "append_job": ["action", "site", "job_title", "category", "client", "deadline", "url", "status"],
    "update_status": ["action", "site", "url", "status"],
}


def setup_logger(run_id: str) -> logging.Logger:
    log_path = LOGS_DIR / f"sync_{run_id}.log"
    logger = logging.getLogger("sync_sheets")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_sheets_service(credentials_path: str):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def get_all_rows(service, spreadsheet_id: str, sheet_name: str) -> list[list]:
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A:N")
        .execute()
    )
    return result.get("values", [])


def ensure_header(service, spreadsheet_id: str, sheet_name: str, header: list[str], logger: logging.Logger):
    rows = get_all_rows(service, spreadsheet_id, sheet_name)
    if not rows or rows[0] != header:
        logger.info("ヘッダー行を設定します")
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [header]},
        ).execute()


def find_row_by_url(rows: list[list], url: str, url_col_idx: int) -> int | None:
    """URLをキーに行インデックス（0始まり）を返す。見つからなければ None"""
    for i, row in enumerate(rows):
        if len(row) > url_col_idx:
            cell = row[url_col_idx]
            # HYPERLINK形式 =HYPERLINK("url","表示") からURLを抽出して比較
            if cell.startswith('=HYPERLINK("') or cell.startswith("=HYPERLINK(\""):
                start = cell.index('"') + 1
                end = cell.index('"', start)
                cell_url = cell[start:end]
            else:
                cell_url = cell
            if cell_url == url:
                return i
    return None


def make_hyperlink(url: str, label: str = "") -> str:
    display = label if label else url
    return f'=HYPERLINK("{url}","{display}")'


def validate_record(record: dict, logger: logging.Logger) -> tuple[bool, str]:
    action = record.get("action")
    if action not in REQUIRED_FIELDS:
        return False, f"未対応のアクション: {action!r}"
    for field in REQUIRED_FIELDS[action]:
        if not record.get(field):
            return False, f"必須フィールド不足: {field}"
    return True, ""


def process_append_job(service, spreadsheet_id: str, sheet_name: str, config: dict, record: dict, logger: logging.Logger):
    cols = config["columns"]
    rows = get_all_rows(service, spreadsheet_id, sheet_name)

    # 重複チェック
    existing_idx = find_row_by_url(rows, record["url"], cols["url"])
    if existing_idx is not None:
        logger.warning(f"重複案件をスキップ: {record['url']} (行 {existing_idx + 1})")
        return

    # No. の採番（ヘッダー行を除いたデータ行数 + 1）
    data_rows = [r for r in rows if r and r[0] != config["header_row"][0]]
    next_no = len(data_rows) + 1

    new_row = [""] * config["column_count"]
    new_row[cols["no"]] = next_no
    new_row[cols["job_title"]] = record.get("job_title", "")
    new_row[cols["category"]] = record.get("category", "")
    new_row[cols["reward_min"]] = record.get("reward_min", "")
    new_row[cols["reward_max"]] = record.get("reward_max", "")
    new_row[cols["client"]] = record.get("client", "")
    new_row[cols["applications"]] = record.get("applications", "")
    new_row[cols["contracts"]] = record.get("contracts", "")
    new_row[cols["deadline"]] = record.get("deadline", "")
    new_row[cols["url"]] = make_hyperlink(record["url"], record.get("job_title", record["url"]))
    new_row[cols["applied_at"]] = record.get("applied_at", "")
    new_row[cols["status"]] = record.get("status", "未応募")
    new_row[cols["result"]] = record.get("result", "")
    new_row[cols["memo"]] = record.get("memo", "")

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [new_row]},
    ).execute()
    logger.info(f"append_job 完了: No.{next_no} {record['job_title']}")


def process_update_status(service, spreadsheet_id: str, sheet_name: str, config: dict, record: dict, logger: logging.Logger):
    cols = config["columns"]
    rows = get_all_rows(service, spreadsheet_id, sheet_name)

    row_idx = find_row_by_url(rows, record["url"], cols["url"])
    if row_idx is None:
        raise ValueError(f"URLに一致する行が見つかりません: {record['url']}")

    sheet_row = row_idx + 1  # Sheetsは1始まり

    updates = []

    # 応募ステータス更新
    status_col_letter = col_index_to_letter(cols["status"])
    updates.append({
        "range": f"{sheet_name}!{status_col_letter}{sheet_row}",
        "values": [[record["status"]]],
    })

    # 応募日更新（指定がある場合のみ）
    if record.get("applied_at"):
        applied_at_col_letter = col_index_to_letter(cols["applied_at"])
        updates.append({
            "range": f"{sheet_name}!{applied_at_col_letter}{sheet_row}",
            "values": [[record["applied_at"]]],
        })

    # メモ更新（指定がある場合のみ）
    if record.get("memo"):
        memo_col_letter = col_index_to_letter(cols["memo"])
        existing_memo = rows[row_idx][cols["memo"]] if len(rows[row_idx]) > cols["memo"] else ""
        new_memo = f"{existing_memo}\n{record['memo']}".strip() if existing_memo else record["memo"]
        updates.append({
            "range": f"{sheet_name}!{memo_col_letter}{sheet_row}",
            "values": [[new_memo]],
        })

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": "USER_ENTERED", "data": updates},
    ).execute()
    logger.info(f"update_status 完了: {record['url']} -> {record['status']}")


def col_index_to_letter(idx: int) -> str:
    """0始まりのカラムインデックスをA1記法の列文字に変換"""
    result = ""
    n = idx
    while True:
        result = chr(ord("A") + n % 26) + result
        n = n // 26 - 1
        if n < 0:
            break
    return result


def process_file(filepath: Path, service, config: dict, logger: logging.Logger) -> tuple[int, int]:
    spreadsheet_id = config["spreadsheet_id"]
    sheet_name = config["sheet_names"]["job_list"]
    success_count = 0
    error_count = 0

    with open(filepath, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"{filepath.name}:{line_no} JSONパースエラー: {e}")
                error_count += 1
                continue

            valid, err_msg = validate_record(record, logger)
            if not valid:
                logger.error(f"{filepath.name}:{line_no} バリデーションエラー: {err_msg} | {line}")
                error_count += 1
                continue

            try:
                action = record["action"]
                if action == "append_job":
                    process_append_job(service, spreadsheet_id, sheet_name, config, record, logger)
                elif action == "update_status":
                    process_update_status(service, spreadsheet_id, sheet_name, config, record, logger)
                success_count += 1
            except HttpError as e:
                logger.error(f"{filepath.name}:{line_no} Sheets APIエラー: {e}")
                error_count += 1
            except Exception as e:
                logger.error(f"{filepath.name}:{line_no} 処理エラー: {e}")
                error_count += 1

    return success_count, error_count


def move_file(src: Path, dest_dir: Path, logger: logging.Logger):
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    # 同名ファイルが既にある場合はタイムスタンプを付与
    if dest.exists():
        stem = src.stem
        suffix = src.suffix
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest_dir / f"{stem}_{ts}{suffix}"
    shutil.move(str(src), str(dest))
    logger.info(f"{src.name} -> {dest_dir.name}/{dest.name}")


def export_applied_urls(service, spreadsheet_id: str, sheet_name: str, config: dict, logger: logging.Logger):
    """スプレッドシートから応募済URLを読み取り applied_urls.txt に書き出す"""
    rows = get_all_rows(service, spreadsheet_id, sheet_name)
    cols = config["columns"]
    applied_urls = []

    for row in rows[1:]:  # ヘッダー行をスキップ
        if len(row) <= max(cols["url"], cols["status"]):
            continue
        status = row[cols["status"]] if len(row) > cols["status"] else ""
        if status in ("応募済", "応募済み"):
            cell = row[cols["url"]] if len(row) > cols["url"] else ""
            # HYPERLINK形式からURLを抽出
            if cell.startswith('=HYPERLINK("'):
                start = cell.index('"') + 1
                end = cell.index('"', start)
                url = cell[start:end]
            else:
                url = cell
            if url:
                applied_urls.append(url)

    output_path = BASE_DIR / "applied_urls.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(applied_urls))
    logger.info(f"applied_urls.txt を更新: {len(applied_urls)}件の応募済URL")


def main():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(run_id)

    logger.info("=== 同期処理開始 ===")

    config = load_config()

    if config["spreadsheet_id"] == "YOUR_SPREADSHEET_ID_HERE":
        logger.error("config.json の spreadsheet_id を設定してください")
        sys.exit(1)

    credentials_path = BASE_DIR / config["credentials_path"]
    if not credentials_path.exists():
        logger.error(f"認証ファイルが見つかりません: {credentials_path}")
        sys.exit(1)

    try:
        service = get_sheets_service(str(credentials_path))
    except Exception as e:
        logger.error(f"Sheets サービス初期化失敗: {e}")
        sys.exit(1)

    # ヘッダー確認・設定
    sheet_name = config["sheet_names"]["job_list"]
    try:
        ensure_header(service, config["spreadsheet_id"], sheet_name, config["header_row"], logger)
    except Exception as e:
        logger.error(f"ヘッダー設定失敗: {e}")
        sys.exit(1)

    # 応募済URLリストを書き出す（inboxが空でも常に最新を維持）
    try:
        export_applied_urls(service, config["spreadsheet_id"], sheet_name, config, logger)
    except Exception as e:
        logger.warning(f"applied_urls.txt の書き出し失敗: {e}")

    # inbox の jsonl ファイルを処理
    inbox_files = sorted(INBOX_DIR.glob("*.jsonl"))
    if not inbox_files:
        logger.info("inbox/ に処理対象ファイルなし")
        logger.info("=== 同期処理終了 ===")
        return

    total_success = 0
    total_error = 0
    for filepath in inbox_files:
        logger.info(f"処理開始: {filepath.name}")
        try:
            success, error = process_file(filepath, service, config, logger)
            total_success += success
            total_error += error

            if error == 0:
                move_file(filepath, PROCESSED_DIR, logger)
            else:
                # エラーがあっても成功分は反映済み。ファイルは error へ移動
                logger.warning(f"{filepath.name}: {error}件のエラーあり -> error/ へ移動")
                move_file(filepath, ERROR_DIR, logger)
        except Exception as e:
            logger.error(f"{filepath.name}: ファイル処理中に致命的エラー: {e}")
            move_file(filepath, ERROR_DIR, logger)

    logger.info(f"=== 同期処理終了: 成功 {total_success}件 / エラー {total_error}件 ===")

    # 追加後も再度書き出して最新状態を維持
    try:
        export_applied_urls(service, config["spreadsheet_id"], sheet_name, config, logger)
    except Exception as e:
        logger.warning(f"applied_urls.txt の再書き出し失敗: {e}")


if __name__ == "__main__":
    main()
