#!/usr/bin/env python3
"""
案件応募自動化システム - Google Sheets 同期スクリプト（GAS版）
役割: inbox/ の _applied.jsonl を読み取り、GAS Web App 経由で Google Sheets に反映する
認証: 不要（GAS Web App のURL自体が秘密鍵の役割）
"""

import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import requests

# ---- パス設定 ----
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "inbox"
PROCESSED_DIR = BASE_DIR / "processed"
ERROR_DIR = BASE_DIR / "error"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_PATH = BASE_DIR / "config.json"


def setup_logger(run_id: str) -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
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


def send_to_gas(gas_url: str, records: list[dict], logger: logging.Logger) -> bool:
    """GAS Web App にPOSTしてスプシに書き込む"""
    try:
        r = requests.post(gas_url, json=records, timeout=30)
        if r.status_code == 200:
            result = r.json()
            logger.info(f"GAS送信成功: {result.get('count', 0)}件")
            return True
        else:
            logger.error(f"GAS送信失敗: status={r.status_code} body={r.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        logger.error("GAS送信タイムアウト（30秒）")
        return False
    except Exception as e:
        logger.error(f"GAS送信エラー: {e}")
        return False


def process_file(filepath: Path, logger: logging.Logger) -> list[dict]:
    """applied.jsonlを読み込んで送信用レコードのリストを返す"""
    records = []
    with open(filepath, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"{filepath.name}:{line_no} JSONパースエラー: {e}")
                continue

            action = record.get("action")
            if action != "append_job":
                logger.info(f"{filepath.name}:{line_no} スキップ（action={action}）")
                continue

            records.append({
                "site": record.get("site", ""),
                "job_title": record.get("job_title", ""),
                "category": record.get("category", ""),
                "reward_min": record.get("reward_min", ""),
                "reward_max": record.get("reward_max", ""),
                "client": record.get("client", ""),
                "applications": record.get("applications", ""),
                "contracts": record.get("contracts", ""),
                "deadline": record.get("deadline", ""),
                "url": record.get("url", ""),
                "applied_at": record.get("applied_at", ""),
                "status": record.get("status", ""),
                "result": record.get("result", ""),
                "memo": record.get("memo", ""),
            })

    return records


def move_file(src: Path, dest_dir: Path, logger: logging.Logger):
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if dest.exists():
        stem = src.stem
        suffix = src.suffix
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = dest_dir / f"{stem}_{ts}{suffix}"
    shutil.move(str(src), str(dest))
    logger.info(f"{src.name} -> {dest_dir.name}/{dest.name}")


def main():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = setup_logger(run_id)

    logger.info("=== スプシ同期処理開始 ===")

    config = load_config()
    gas_url = config.get("gas_url", "")

    if not gas_url:
        logger.error("config.json に gas_url が設定されていません")
        sys.exit(1)

    # inbox の _applied.jsonl ファイルのみ処理
    inbox_files = sorted(INBOX_DIR.glob("*_applied.jsonl"))
    if not inbox_files:
        logger.info("inbox/ に処理対象ファイルなし")
        logger.info("=== スプシ同期処理終了 ===")
        return

    total_sent = 0
    for filepath in inbox_files:
        logger.info(f"処理開始: {filepath.name}")
        records = process_file(filepath, logger)

        if not records:
            logger.info(f"{filepath.name}: 送信対象なし")
            move_file(filepath, PROCESSED_DIR, logger)
            continue

        success = send_to_gas(gas_url, records, logger)
        if success:
            total_sent += len(records)
            move_file(filepath, PROCESSED_DIR, logger)
        else:
            move_file(filepath, ERROR_DIR, logger)

    logger.info(f"=== スプシ同期処理終了: {total_sent}件送信 ===")


if __name__ == "__main__":
    main()
