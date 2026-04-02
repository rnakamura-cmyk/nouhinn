# 案件応募スキル - パイプラインルーター

## 設計思想

全フェーズを Claude Code + Chrome MCP で実行する。
各サイトごとに Phase 1→2→3 を直列実行し、Phase 4（スプシ同期）は全サイト完了後にまとめて実行する。

---

## ルーティングルール

### スクレイピング+応募文作成（Phase 1→2）

以下を順番に実行する：
1. `SCRAPE_SKILL.md` → 応募可能な3件を収集
2. `DRAFT_SKILL.md` → 3件分の応募文を生成

### 応募（Phase 3）

1. `APPLY_SKILL.md` → 3件をフォーム送信

### スプシ同期（Phase 4）

`inbox/` にある `*_applied.jsonl` を読み取り、`config.json` の `gas_url` にPOSTする。

手順：
1. `config.json` を読み込み `gas_url` を取得
2. `inbox/` から `*_applied.jsonl` ファイルを探す
3. 各ファイルのJSONLを読み、`action` が `append_job` のレコードだけ抽出
4. 抽出したレコードをまとめて `gas_url` に `curl` でPOST：
   ```bash
   curl -s -L -X POST -H "Content-Type: application/json" -d '{JSONデータ}' '{gas_url}'
   ```
5. 成功したら該当ファイルを `processed/` に移動
6. 失敗したら `error/` に移動

### 個別実行も可能

| 指示 | 実行内容 |
|------|---------|
| 「スクレイピングを実行」 | `SCRAPE_SKILL.md` |
| 「応募文を作成」 | `DRAFT_SKILL.md` |
| 「応募を実行」 | `APPLY_SKILL.md` |
| 「スプシ同期」 | 上記 Phase 4 の手順 |

---

## 対象サイト

| 指示に含まれるキーワード | サイト名（フォルダ名） |
|------------------------|-------------------|
| スキルシフト / skillshift / skill-shift | `skillshift` |
| ハイプロ / hipro / HiPro Direct | `hipro` |
| チイキズカン / chiikizukan | `chiikizukan` |

---

## ファイルの流れ

```
Phase 1: SCRAPE（3件で打ち切り）
  └→ inbox/{site}_{timestamp}_candidates.jsonl

Phase 2: DRAFT（candidatesの全件＝3件分を生成）
  └→ inbox/{site}_{timestamp}_drafts.jsonl

Phase 3: APPLY（draftsの全件＝3件分を送信）
  ├→ inbox/{site}_{timestamp}_applied.jsonl
  └→ applied_urls.txt に追記（1件ごと即時）

Phase 4: SYNC
  ├→ applied.jsonl をスプシに反映（curl でGAS URLにPOST）
  └→ processed/ に移動
```

---

## 重複防止

- applied_urls.txt に応募済みURLを蓄積
- Phase 1: 一覧取得時にapplied_urls.txtと照合 → 応募済みはスキップ（3件にカウントしない）
- Phase 3: 送信前にもapplied_urls.txtをダブルチェック
- Phase 3: 1件送信するごとに即座にapplied_urls.txtに追記 → クラッシュしても安全

---

## 軽量化ポイント

- 毎日回す前提 → 上から3件取れば十分（新着が入れば自然にカバー）
- 3件収集→3件生成→3件応募（無駄ゼロ）
- 直列実行でバトンファイル待ちの空白時間なし
- Chrome MCPでDOM直接操作（Computer Useより高速・軽量）
- Python不要。スプシ同期もcurlで直接GASにPOST

---

## 注意事項

- 各サイトには事前にブラウザでログインしておくこと
- PCの電源が入っている必要がある（ローカル実行のため）
- candidates.jsonl と drafts.jsonl は sync 処理の対象外（action が "candidate" / "draft" のためスキップ）
