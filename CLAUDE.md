# 案件応募自動化システム

副業サイト（チイキズカン・スキルシフト・ハイプロ）で案件を自動検索・応募し、結果をGoogleスプレッドシートに記録するシステムです。
毎日自動実行し、気付いたら案件が溜まっている設計。

## Claude Codeへの指示

**このファイルを読んだら、まず以下のメッセージをユーザーに送ってください。他のステップは何もせず、返答を待ってください。**

---

```
案件応募自動化システムへようこそ！

3つの副業サイト（チイキズカン・スキルシフト・ハイプロ）に
毎日自動で応募し、結果をスプレッドシートに記録するシステムです。

セットアップを始めますか？
（プロフィール入力・スプシ連携・スケジュール設定まで一緒にやります）

y で進める / n でキャンセル
```

---

**「n」が返ってきたら「了解です。必要なときはいつでも声をかけてください。」と伝えて終了してください。**

---

**「y」が返ってきたら、以下のフェーズを順番に実行してください。**

---

## フェーズ1：環境セットアップ

### 1-1. gitの確認

```bash
git --version
```
失敗 → gitのインストールを案内。

---

### 1-2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```
失敗したら `pip3 install -r requirements.txt` を試す。

---

### 1-3. システムパスの自動検出

`config.json` の `base_dir` に、このフォルダの絶対パスを書き込む。

表示されたパスをユーザーに確認。

---

## フェーズ2：プロフィール設定

以下の質問を**1つずつ**聞く。まとめて聞かず、返答を受けてから次へ。

**Q1** あなたのお名前を教えてください。
**Q2** 略歴を教えてください。（経歴・得意なこと・実績など）
**Q3** なぜ副業案件をやりたいですか？（志望動機）
**Q4** 志望する職種・キーワード・業界を教えてください。（例：経営企画、DX支援、地方創生など）
**Q5** やりたくない仕事の条件はありますか？（NG条件）
**Q6** 希望の稼働時間はありますか？（任意・スキップOK）

全回答を `my_profile.md` に書き出す：

```markdown
# プロフィール

## 基本情報
- 名前: {Q1}

## 略歴
{Q2}

## 志望動機
{Q3}

## 志望職種・キーワード・業界
{Q4を箇条書き}

## NG条件
{Q5を箇条書き}

## 希望条件
{Q6}

## 応募文スタイル
- 「{Q1の名前}」と記載する（ニックネーム・略称は使わない）
- Q2の経歴・実績を具体的に引用する
- Q3の志望動機を案件内容に紐づけて記述する
- 推測や嘘の実績は絶対に書かない
- 冒頭は「はじめまして、{名前}と申します。」
- 末尾は「ぜひ一度、詳細をお聞かせください。」で締める
```

**さらに、Q4の回答をもとに以下のファイルを更新する：**

- `pipeline_config.json` の `search.categories` にQ4の職種・業界を反映
- `sites/chiikizukan/config.json` の `search_filters.preferred_keywords` にQ4のキーワードを反映
- `sites/skillshift/config.json` の `search_filters.preferred_keywords` にQ4のキーワードを反映
- `sites/hipro/config.json` の `search_filters.preferred_keywords` にQ4のキーワードを反映

**Q5の回答をもとに以下を更新する：**

- `pipeline_config.json` の `apply_criteria.ng_keywords` にQ5のNG条件を反映
- 各サイトの `config.json` の `apply_criteria.ng_keywords` にも同様に反映

---

## フェーズ3：Googleスプレッドシート + GAS の設定

ユーザーにこう伝える：

```
次に、応募結果を記録するGoogleスプレッドシートを設定します。

1. https://sheets.new で新しいスプレッドシートを作成
2. シート名（下のタブ）を「案件管理」に変更
3. 「拡張機能」→「Apps Script」を開く
4. 既存のコードを全部消して、以下のコードを貼り付け：
```

以下のコードをユーザーに提示する：

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("案件管理");
  var data = JSON.parse(e.postData.contents);

  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "No.", "サイト名", "案件名", "カテゴリ", "報酬（下限）", "報酬（上限）",
      "クライアント", "応募数", "契約状況", "締切日", "URL",
      "応募日", "ステータス", "結果", "メモ"
    ]);
  }

  var rows = Array.isArray(data) ? data : [data];

  rows.forEach(function(row) {
    var no = sheet.getLastRow();
    sheet.appendRow([
      no,
      row.site || "",
      row.job_title || "",
      row.category || "",
      row.reward_min || "",
      row.reward_max || "",
      row.client || "",
      row.applications || "",
      row.contracts || "",
      row.deadline || "",
      row.url || "",
      row.applied_at || "",
      row.status || "",
      row.result || "",
      row.memo || ""
    ]);
  });

  return ContentService.createTextOutput(
    JSON.stringify({ status: "ok", count: rows.length })
  ).setMimeType(ContentService.MimeType.JSON);
}
```

続けて案内：

```
5. 「デプロイ」→「新しいデプロイ」
6. 種類：ウェブアプリ
7. アクセスできるユーザー：「全員」
8. 「デプロイ」をクリック → アクセスを承認
9. 表示されるURLをここに貼り付けてください
```

URLを受け取ったら `config.json` の `gas_url` を更新する。

### 動作確認

```bash
python sync_sheets.py
```

「inbox/ に処理対象ファイルなし」と表示されれば成功。
エラーが出た場合は `config.json` の `gas_url` が正しいか確認する。

---

## フェーズ4：サイトログイン確認

ユーザーにこう伝える：

```
以下の3サイトにブラウザでログインしてください：

1. チイキズカン: https://chiiki-zukan.com/
2. スキルシフト: https://www.skill-shift.com/
3. ハイプロ Direct: https://talent.direct.hipro-job.jp/talent/

ログインしたら「完了」と教えてください。
```

---

## フェーズ5：スケジュール設定

ユーザーにこう伝える：

```
最後に、毎日の自動応募スケジュールを設定します。

毎日PCをオンにできる時間帯を教えてください。
（例：8時〜12時、9時〜11時など）
```

回答を受けたら、その時間帯に収まるように**1時間ずつ3サイト分**のタスクを配置する。
各サイトは一気通貫（スクレイピング→応募文作成→応募→スプシ同期）で1タスク。

例：ユーザーが「8時〜12時」と答えた場合：

```
08:00  チイキズカン（一気通貫）
09:00  スキルシフト（一気通貫）
10:00  ハイプロ（一気通貫）
```

`mcp__scheduled-tasks__create_scheduled_task` でスケジュールタスクを作成する。
各タスクのプロンプトは以下の形式：

```
{サイト名}で、スクレイピング→応募文作成→応募実行→スプシ同期を順番に実行してください。
作業ディレクトリ: {base_dir}
```

**注意：初回実行時にツール許可プロンプトが出る。「Always allow」を押せば以降は自走する。**
タスク作成後、ユーザーに「1つ目のタスクを Run now して、許可を全部通してください」と案内する。

---

## フェーズ6：デモ実行 & 完了

スケジュール設定後、ユーザーにこう伝える：

```
セットアップ完了まであと一歩です！
実際にチイキズカンで1件だけ応募して動作確認しますか？

y で実行 / n でスキップ
```

**「n」が返ってきたら** → フェーズ6をスキップして完了メッセージへ。

**「y」が返ってきたら** → このセッション内で直接パイプラインを実行する：

1. `SCRAPE_SKILL.md` に従いチイキズカンで候補を収集
2. `DRAFT_SKILL.md` に従い応募文を生成
3. `APPLY_SKILL.md` に従いフォーム送信
4. `python sync_sheets.py` を実行してスプシに反映

（※ `claude --dangerously-skip-permissions -p` はClaude Code内からは実行できないため、直接実行する）

完了したら以下を伝える：

```
セットアップ完了です！

チイキズカンへの応募が完了しました。
スプレッドシートを確認してみてください。こんな風に毎日応募結果が溜まっていきます。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【重要な注意点】
- PCの電源が入っていること
- 3サイトにブラウザでログインした状態を維持すること

この2つが毎日の自動応募の条件です。
明日から自動で回り始めます！
```

---

## ファイル構成

```
案件自動応募/
├── CLAUDE.md              ← このファイル（セットアップ案内）
├── PIPELINE_SKILL.md      ← パイプライン実行ルーター
├── SCRAPE_SKILL.md        ← Phase 1: 候補収集（上から20件→最大3件）
├── DRAFT_SKILL.md         ← Phase 2: 応募文作成
├── APPLY_SKILL.md         ← Phase 3: フォーム送信
├── sync_sheets.py         ← Phase 4: GAS経由スプシ同期
├── my_profile.md          ← プロフィール（セットアップで生成・.gitignore対象）
├── config.json            ← GAS URL・カラム定義
├── pipeline_config.json   ← 検索条件・応募基準
├── applied_urls.txt       ← 応募済みURL（重複防止・.gitignore対象）
├── sites/
│   ├── chiikizukan/       ← サイト別設定（config.json + SKILL.md）
│   ├── skillshift/
│   └── hipro/
├── inbox/                 ← 各フェーズの出力（jsonl）
├── processed/             ← 処理済みファイル
├── error/                 ← エラーファイル
└── logs/                  ← 実行ログ
```

---

## 日常の運用

毎日自動で以下を実行：
1. 3サイトから候補を収集（各3件）
2. プロフィールに合わせて応募文を自動生成
3. 各サイト最大3件ずつ応募（合計9件/日）
4. 結果をスプレッドシートに記録

**人間がやること：PCの電源を入れておく・各サイトのログインを維持するだけ。**
