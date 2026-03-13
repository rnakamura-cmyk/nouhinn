# 案件応募スキル（ルーター）

## トリガー例
```
案件応募を実行してください。クラウドワークスで、GAS・業務自動化カテゴリのみで。
案件応募を実行してください。スキルシフトで、AI活用カテゴリで。
案件応募を実行してください。クラウドワークスとスキルシフト両方で。
```

---

## Step 1. 対象サイトを特定する

指示文からサイトを判断して、該当フォルダのファイルを読み込む：

| 指示に含まれるキーワード | 参照フォルダ |
|------------------------|-------------|
| クラウドワークス / crowdworks / CW | `sites/crowdworks/` |
| スキルシフト / skillshift / skill-shift | `sites/skillshift/` |

読み込むファイル：
- `/Users/ryonkook/自動応募/automation_bridge/sites/{サイト名}/config.json`
- `/Users/ryonkook/自動応募/automation_bridge/sites/{サイト名}/SKILL.md`
- `/Users/ryonkook/自動応募/automation_bridge/my_profile.md`（共通）

カテゴリ指定がある場合は config.json の categories より優先する。

---

## Step 2. 応募済みURLリストを読む（重複応募防止）

`/Users/ryonkook/自動応募/automation_bridge/applied_urls.txt` を読み込む。
このファイルに含まれるURLは **サイト問わず必ずスキップ** する。
ファイルが存在しない場合は空リストとして扱い続行する。

---

## Step 3. サイト別手順に従って実行する

読み込んだ `sites/{サイト名}/SKILL.md` の手順に従って：
1. ログイン済みブラウザでサイトにアクセス
2. 案件を検索
3. 応募判断（下記の共通基準を適用）
4. 応募文を自動生成（my_profile.md と案件内容を照合）
5. フォームを埋めて応募

---

## 共通：応募判断基準

**応募する条件（すべて満たす）：**
- 締切が3日以上ある
- ng_keywords に含まれるキーワードが案件内容にない
- my_profile.md の得意領域と案件内容が1つ以上合っている

**スキップする条件（どれか1つでも当てはまる）：**
- デザイン・翻訳・語学・常駐・対面必須・出社・イラスト・グラフィック
- 締切切れ・すでに終了・applied_urls.txt に含まれるURL
- プロフィールのスキルと全く合わない内容

---

## 共通：応募文の自動生成ルール

1. 案件の詳細ページを読む（タイトル・説明文・求めるスキル）
2. `my_profile.md` の強み・実績と照合する
3. 「この案件のどの部分に自分が貢献できるか」を1〜2点に絞る
4. その案件専用の応募文を生成する

**生成ルール：**
- 冒頭は「はじめまして、むらりょう（中村崚）と申します。」
- 案件内容に直接触れる（「○○の自動化」「○○の立ち上げ支援」など）
- my_profile.md の実績を1つ具体的に引用する
- 300〜400文字程度
- 最後は「ぜひ詳細をお聞かせください」で締める
- 決して推測や嘘の実績を書かない

---

## 共通：結果のjsonl出力

出力先: `/Users/ryonkook/自動応募/automation_bridge/inbox/{サイト名}_YYYYMMDD_HHMMSS.jsonl`

**応募した案件（1件1行）:**
```
{"action":"append_job","site":"サイト名","job_title":"案件名","category":"カテゴリ","reward_min":"下限","reward_max":"上限","client":"クライアント名","applications":応募数,"contracts":"契約状況","deadline":"締切日(YYYY-MM-DD)","url":"案件URL","status":"応募済","applied_at":"今日の日付(YYYY-MM-DD)","result":"","memo":"どのプロフィール項目を使ったか一言"}
```

**スキップした案件（記録のみ）:**
```
{"action":"append_job","site":"サイト名","job_title":"案件名","category":"カテゴリ","reward_min":"","reward_max":"","client":"クライアント名","applications":応募数,"contracts":"契約状況","deadline":"締切日","url":"案件URL","status":"スキップ","applied_at":"","result":"","memo":"スキップ理由"}
```

**ルール：**
- 1レコードは必ず1行で完結させる
- 推測値を入れず、画面から取得した事実のみ書く
- 応募した・しない両方を記録する
