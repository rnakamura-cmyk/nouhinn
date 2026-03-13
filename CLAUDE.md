# 案件応募自動化システム

このシステムは、クラウドワークスなどの副業サイトで案件を自動検索・応募し、結果をGoogleスプレッドシートに記録するツールです。

## セットアップ（Claude Codeがここを読んで案内してください）

**ユーザーが「セットアップして」と言ったら、以下を順番に確認・実行してください。**

---

### Step 1. 必要ファイルの確認

以下のファイルが存在するか確認する：

- [ ] `credentials.json` → なければ Step 2 へ
- [ ] `my_profile.md` → なければ Step 3 へ
- [ ] `config.json` の `spreadsheet_id` が設定済みか → 未設定なら Step 4 へ

---

### Step 2. Google credentials.json の取得（未設定の場合）

ユーザーにこう伝える：

```
以下の手順でGoogle Cloudの認証ファイルを取得してください（10分ほどかかります）：

1. https://console.cloud.google.com/ を開く
2. 新しいプロジェクトを作成（名前は何でもOK）
3. 「APIとサービス」→「ライブラリ」→「Google Sheets API」を有効化
4. 「APIとサービス」→「認証情報」→「サービスアカウントを作成」
   - 名前: job-automation（何でもOK）
   - ロール: 編集者
5. 作成したサービスアカウントをクリック →「キー」タブ →「鍵を追加」→「JSON」
6. ダウンロードしたファイルを credentials.json にリネームして、このフォルダに置く

完了したら「置きました」と教えてください。
```

---

### Step 3. プロフィールファイルの作成

`my_profile.example.md` をコピーして `my_profile.md` を作成し、中身をユーザーの情報に書き換えるよう案内する：

```
cp my_profile.example.md my_profile.md
```

ユーザーに `my_profile.md` を開いて以下を自分の情報に書き換えてもらう：
- ビジネスネーム・キャッチコピー
- 強み・得意領域
- 実績ハイライト
- 応募NG条件

---

### Step 4. スプレッドシートの設定

ユーザーにこう伝える：

```
1. Googleドライブで新しいスプレッドシートを作成してください
2. URLの https://docs.google.com/spreadsheets/d/【ここ】/edit の部分をコピーしてください
3. スプレッドシートの「共有」ボタンを押し、以下のメールアドレスを「編集者」として追加してください：
```

credentials.json の `client_email` を読み取り、ユーザーに表示する。

スプレッドシートIDを受け取ったら `config.json` の `spreadsheet_id` を更新する。

---

### Step 5. Pythonパッケージのインストール

```bash
cd /path/to/automation_bridge
pip install google-auth google-auth-oauthlib google-api-python-client
```

---

### Step 6. 動作テスト

```bash
python3 sync_sheets.py
```

「inbox/ に処理対象ファイルなし」と表示されれば成功。

---

### Step 7. Coworkの設定（ブラウザ自動化側）

ユーザーにこう伝える：

```
Coworkで以下の操作をしてください：

1. Coworkを開く
2. 「新しいタスク」を作成
3. COWORK_SKILL.md の内容をそのままタスクの指示として貼り付ける
4. （任意）/schedule で毎朝9時に自動実行するよう設定
5. 「スリープしない」をオンにする
```

---

## 日常の使い方

### 応募を実行する（Coworkへの指示）

```
# クラウドワークスで応募
案件応募を実行してください。クラウドワークスで、[カテゴリ名]で。

# スキルシフトで応募
案件応募を実行してください。スキルシフトで、[カテゴリ名]で。

# 両方同時
案件応募を実行してください。クラウドワークスとスキルシフト両方で。
```

### スプレッドシートへの同期（Claude Codeへの指示）

Coworkが応募を終えたら：

```
python3 sync_sheets.py
```

または5分ごとに自動実行されるスケジュールタスク「crowdworks-auto-sync」が自動処理します。

---

## ファイル構成

```
automation_bridge/
├── CLAUDE.md              ← このファイル（セットアップ案内）
├── COWORK_SKILL.md        ← Coworkへの指示ルーター
├── my_profile.md          ← あなたの強み・実績（要作成）
├── my_profile.example.md  ← プロフィールの記入例
├── config.json            ← スプレッドシートID・カラム定義
├── sync_sheets.py         ← Google Sheets同期スクリプト
├── requirements.txt       ← 必要なPythonパッケージ
├── sites/
│   ├── crowdworks/        ← クラウドワークス用設定
│   │   ├── config.json
│   │   └── SKILL.md
│   └── skillshift/        ← スキルシフト用設定
│       ├── config.json
│       └── SKILL.md
├── inbox/                 ← Coworkが結果を書き出す場所
├── processed/             ← 処理済みファイルの置き場
├── error/                 ← エラーファイルの退避先
└── logs/                  ← 実行ログ
```

---

## 対応サイトを追加したいとき

```
sites/{サイト名}/config.json  ← 検索条件
sites/{サイト名}/SKILL.md     ← フォームの埋め方
```
の2ファイルを作るだけ。`sync_sheets.py` は変更不要。
