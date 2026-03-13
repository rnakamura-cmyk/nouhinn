# セットアップ手順

## 1. Google Sheets API の有効化

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成（または既存を選択）
3. 「APIとサービス」→「ライブラリ」から **Google Sheets API** を有効化
4. 「APIとサービス」→「認証情報」→「サービスアカウントを作成」
5. キー（JSON形式）をダウンロードし、`automation_bridge/credentials.json` として保存

## 2. スプレッドシートの準備

1. Google スプレッドシートを新規作成
2. シート名を **「案件一覧」** に変更
3. スプレッドシートのURLからIDを取得
   - URL例: `https://docs.google.com/spreadsheets/d/【ここがID】/edit`
4. サービスアカウントのメールアドレス（`credentials.json` 内の `client_email`）を
   スプレッドシートの共有設定で **編集者** として追加

## 3. config.json の更新

`automation_bridge/config.json` を開き、以下を設定:

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",  ← 取得したIDに変更
  "credentials_path": "credentials.json",
  ...
}
```

## 4. 依存パッケージのインストール

```bash
cd automation_bridge
pip install -r requirements.txt
```

または venv を使う場合:

```bash
cd automation_bridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. 動作確認

### テスト用 jsonl を inbox に配置

```bash
cp schemas/append_job_example.jsonl inbox/test_$(date +%Y%m%d).jsonl
```

### 同期スクリプトを実行

```bash
python3 sync_sheets.py
```

### 確認ポイント

- スプレッドシートの「案件一覧」にデータが追加されているか
- URL列が `=HYPERLINK(...)` 形式になっているか
- `processed/` にファイルが移動されているか
- `logs/` にログファイルが生成されているか

---

## ディレクトリ構成

```
automation_bridge/
├── inbox/          # Cowork が出力した未処理ファイル
├── processed/      # 正常処理済みファイル
├── error/          # エラーファイル
├── logs/           # 実行ログ
├── schemas/        # jsonl 仕様サンプル・定義
├── config.json     # 設定ファイル
├── credentials.json # Google API 認証情報（要自分で配置）
├── requirements.txt
├── sync_sheets.py  # メイン同期スクリプト
└── SETUP.md        # このファイル
```

---

## Cowork への依頼文

案件を確認・応募したら、以下の形式で `inbox/` にファイルを出力してください。

### ファイル命名規則

```
inbox/crowdworks_YYYYMMDD_HHMMSS.jsonl
```

### 新規案件追加（append_job）

```json
{"action":"append_job","site":"crowdworks","job_title":"案件名","category":"カテゴリ","reward_min":"","reward_max":"","client":"クライアント名","applications":0,"contracts":"0/1","deadline":"2026-03-31","url":"https://...","status":"未応募","result":"","memo":"メモ"}
```

### ステータス更新（update_status）

```json
{"action":"update_status","site":"crowdworks","url":"https://...","status":"応募済","applied_at":"2026-03-13","memo":"応募完了"}
```

**注意事項:**
- 1レコードは1行で完結させる
- JSONとして正しい形式にする
- 未取得項目は空文字 `""` でよい
- 推測値を入れず、取得した事実のみ出力する
- スプレッドシートのカラム順や数式設計は意識しなくてよい

---

## よくあるエラーと対処

| エラー | 原因 | 対処 |
|--------|------|------|
| `spreadsheet_id を設定してください` | config.json 未設定 | config.json の spreadsheet_id を更新 |
| `認証ファイルが見つかりません` | credentials.json 未配置 | サービスアカウントのJSONをダウンロードして配置 |
| `HttpError 403` | 共有設定未完了 | スプレッドシートにサービスアカウントを編集者追加 |
| `URLに一致する行が見つかりません` | update_status 対象なし | 先に append_job で案件を追加する |
