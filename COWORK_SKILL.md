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
| ハイプロ / hipro / HiPro Direct | `sites/hipro/` |
| ふるさと兼業 / furusatokengyo | `sites/furusatokengyo/` |
| オタノミ / otanomi | `sites/otanomi/` |
| チイキズカン / chiikizukan | `sites/chiikizukan/` |
| ライフル / lifull / LIFULL LOCAL MATCH | `sites/lifull/` |
| ロッツフル / lotsful | `sites/lotsful/` |

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

## Step 3. 案件を検索して候補を収集する（応募はまだしない）

読み込んだ `sites/{サイト名}/SKILL.md` の手順に従ってサイトにアクセスし、案件を検索する。
**このステップでは応募せず、候補の収集のみ行う。**

収集した案件を以下の基準でふるいにかける：

**候補に残す条件（すべて満たす）：**
- 締切が3日以上ある
- ng_keywords に含まれるキーワードが案件内容にない
- my_profile.md の得意領域と案件内容が1つ以上合っている
- applied_urls.txt に含まれていない

**候補から除外する条件（どれか1つでも当てはまる）：**
- デザイン・翻訳・語学・常駐・対面必須・出社・イラスト・グラフィック
- 締切切れ・すでに終了
- プロフィールのスキルと全く合わない内容

---

## Step 4. 候補をチャットに表示してユーザーに確認する

収集した候補案件を以下の形式でチャットに表示し、**応募してよいか確認する**：

```
以下の案件が見つかりました。応募するものを教えてください。

① [案件名]
   報酬: ○○円〜 | 締切: YYYY-MM-DD | 応募数: ○件
   一言: [この案件と自分のどのスキルが合うか一言]

② [案件名]
   報酬: ○○円〜 | 締切: YYYY-MM-DD | 応募数: ○件
   一言: [この案件と自分のどのスキルが合うか一言]

（以下続く...）

「全部」「①③⑤」「①以外」などの形式で教えてください。
スキップしたい場合は「なし」と教えてください。
```

---

## Step 5. ユーザーの返答を受けて応募実行する

ユーザーの返答に従い、指定された案件のみ応募する。

各案件について：
1. 案件詳細ページを開く
2. 応募文を自動生成（下記ルールに従う）
3. フォームを埋めて応募送信

応募文の生成ルール：
- 冒頭は「はじめまして、むらりょう（中村崚）と申します。」
- 案件内容に直接触れる（「○○の自動化」「○○の立ち上げ支援」など）
- my_profile.md の実績を1つ具体的に引用する
- 300〜400文字程度
- 最後は「ぜひ詳細をお聞かせください」で締める
- 決して推測や嘘の実績を書かない

---

## Step 6. 結果をjsonlで出力する

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
