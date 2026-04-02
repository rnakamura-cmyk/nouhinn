# 応募文作成スキル（Phase 2：テキスト生成）

## トリガー例
```
応募文を作成してください。スキルシフトで。
ドラフトを作成してください。チイキズカンで。
```

## 目的
`_candidates.jsonl` を読み込み、各案件の応募文を生成して `_drafts.jsonl` に保存する。
**このフェーズではブラウザを使わない。ファイルの読み書きだけ。**

---

## Step 0. パスを取得

`config.json` の `base_dir` を読み込む。空欄の場合はこのファイルのフォルダパスを使う。

---

## Step 1. 対象サイトを特定

指示文からサイトを判断して以下を読み込む：

| 指示に含まれるキーワード | 参照フォルダ |
|------------------------|-------------|
| スキルシフト / skillshift | `{base_dir}/sites/skillshift/` |
| ハイプロ / hipro / HiPro Direct | `{base_dir}/sites/hipro/` |
| チイキズカン / chiikizukan | `{base_dir}/sites/chiikizukan/` |

読み込むファイル：
- `{base_dir}/sites/{サイト名}/config.json`
- `{base_dir}/sites/{サイト名}/SKILL.md`（フォーム仕様を確認するため）
- `{base_dir}/my_profile.md`

---

## Step 2. candidates.jsonl を探す

`{base_dir}/inbox/` から `{サイト名}_*_candidates.jsonl` を探す。

- 複数ある場合は**ファイル名の日時が最新のもの**を使う
- 見つからない場合：
  ```
  {サイト名} の candidates.jsonl が見つかりません。
  先にスクレイピングを実行してください。
  ```
  と出力して終了。

---

## Step 3. 応募済みURLを確認

`{base_dir}/applied_urls.txt` を読み込む。存在しない場合は空リスト。
既に応募済みのURLはスキップ対象としてマークする。

---

## Step 4. 各案件の応募文を生成

candidates.jsonl の内容を **上から順に** 読み込む（Phase 1で既に3件に絞られている）。

各案件について以下を生成する：

### スキルシフトの場合（2フィールド）

| フィールド | 文字数 | 生成ルール |
|-----------|--------|----------|
| self_pr | 300〜800文字 | my_profile.md の得意領域・実績を案件に合わせてアレンジ |
| motivation | 300〜800文字 | 案件内容に直接触れた志望理由。実績を1つ引用 |

### チイキズカンの場合（1フィールド）

| フィールド | 文字数 | 生成ルール |
|-----------|--------|----------|
| essay | 200〜500文字 | 経験の活かし方 + 地域課題解決への貢献意欲 |

### ハイプロの場合（1フィールド）

| フィールド | 文字数 | 生成ルール |
|-----------|--------|----------|
| comment | 300〜800文字 | 惹かれた理由 + 参加した際にできること |

### 応募文の共通ルール

- 冒頭: `my_profile.md` の名前を使い「はじめまして、{名前}と申します。」
- 案件内容に直接触れる（案件名・キーワードを引用）
- `my_profile.md` の実績を1つ具体的に引用
- 推測や嘘の実績は絶対に書かない
- `my_profile.md` の「応募文スタイル」セクションに従う
- 末尾: 「ぜひ一度、詳細をお聞かせください。」

---

## Step 5. drafts.jsonl を出力

出力先: `{base_dir}/inbox/{サイト名}_{candidatesのタイムスタンプ}_drafts.jsonl`

**タイムスタンプは candidates.jsonl と同じものを使う**（バトンの対応関係を維持）。

各行フォーマット（1件1行）：

### スキルシフト
```
{"action":"draft","site":"skillshift","url":"案件URL","job_title":"案件名","status":"draft","self_pr":"生成した自己PR","motivation":"生成した志望理由","skip_reason":""}
```

### チイキズカン
```
{"action":"draft","site":"chiikizukan","url":"案件URL","job_title":"案件名","status":"draft","essay":"生成したエッセイ","skip_reason":""}
```

### ハイプロ
```
{"action":"draft","site":"hipro","url":"案件URL","job_title":"案件名","status":"draft","comment":"生成したコメント","skip_reason":""}
```

### スキップする案件
```
{"action":"draft","site":"サイト名","url":"案件URL","job_title":"案件名","status":"skip","skip_reason":"応募済み / NG条件該当 等"}
```

---

## Step 6. 完了報告

```
{サイト名}: X件の応募文を作成しました（スキップ Y件）
drafts.jsonl を inbox/ に保存しました。
```

---

## 注意事項

- **ブラウザは絶対に使わない**。ファイルの読み書きだけで完結する
- 1レコードは必ず1行で完結させる（改行を含めない）
- candidates.jsonl に記載された情報だけで応募文を作る（一覧ページの情報のみ）
- 案件の詳細ページは Phase 3（APPLY）で確認する
