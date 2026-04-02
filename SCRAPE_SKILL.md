# スクレイピングスキル（Phase 1：候補収集）

## トリガー例
```
スクレイピングを実行してください。スキルシフトで。
候補案件を収集してください。ハイプロで。
```

## 目的
サイトにアクセスして候補案件を収集し `_candidates.jsonl` に保存する。
**このフェーズでは応募しない。ページを読むだけ。**

---

## ブラウザルール（最重要）

1. **新しいタブを開かない** - 既に開いているタブを使う
2. **既存のログイン済みセッションを使う** - 新しくURLを開いてログインし直さない
3. 操作する前に、まず現在のタブ一覧を確認する
4. 対象サイトが開いているタブがあれば、そのタブに切り替えて使う
5. 対象サイトのタブがない場合のみ、既存タブの1つでURLを開く

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
- `{base_dir}/sites/{サイト名}/SKILL.md`
- `{base_dir}/my_profile.md`

---

## Step 2. 応募済みURLを読む

`{base_dir}/applied_urls.txt` を読み込む。存在しない場合は空リスト。

---

## Step 3. サイトにアクセスして案件一覧を収集

SKILL.md の手順に従いサイトにアクセスし、案件一覧ページを読み取る。
**詳細ページは開かない（速度優先）。一覧ページで取得できる情報のみを使う。**

一覧で判断できる除外条件（1つでも該当したら除外）：
- `applied_urls.txt` にURLが含まれる
- タイトルに `ng_keywords` のいずれかが含まれる
- 締切が今日以前

---

## Step 4. candidates.jsonl を出力

出力先: `{base_dir}/inbox/{サイト名}_{YYYYMMDD_HHMMSS}_candidates.jsonl`

各行フォーマット（1件1行、推測値は入れない）：
```
{"action":"candidate","site":"サイト名","url":"案件URL","job_title":"案件名","category":"カテゴリ","reward_min":"","reward_max":"","client":"クライアント名","deadline":"YYYY-MM-DD","applications":応募数,"score":スコア,"match_reason":"スコア根拠"}
```

**scoreの計算（0〜3）：**
- `+1`: `preferred_keywords` にタイトルが合致
- `+1`: `my_profile.md` の得意領域とタイトルが合致
- `+1`: 締切が7日以上ある

---

## Step 5. 完了報告

```
{サイト名}: X件の候補を inbox/ に保存しました（高優先度 Y件 / 通常 Z件）
```

---

## 注意事項

- `candidates.jsonl` はスプレッドシートに反映しない（action が "candidate" のため sync_sheets.py がスキップする）
- 同一サイトの今日付けファイルが既にある場合は上書きせず新規作成（タイムスタンプが違うので問題なし）
