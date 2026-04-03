# 案件応募スキル - パイプラインルーター

## 設計思想

全フェーズを Claude Code + Chrome MCP で実行する。
各サイトごとに Phase 1→2→3→4 を直列実行する（一気通貫）。

---

## 一撃プロンプト集

### サイト別一気通貫（スケジュール登録用）
```
チイキズカンで、スクレイピング→応募文作成→応募実行→スプシ同期を順番に実行してください。
```
```
スキルシフトで、スクレイピング→応募文作成→応募実行→スプシ同期を順番に実行してください。
```
```
ハイプロで、スクレイピング→応募文作成→応募実行→スプシ同期を順番に実行してください。
```

### 個別フェーズ実行
```
スクレイピングを実行してください。チイキズカンで。
```
```
応募文を作成してください。チイキズカンで。
```
```
応募を実行してください。チイキズカンで。
```
```
スプシ同期してください。
```

---

## ルーティングルール

### 一気通貫プロンプト（「スクレイピング→応募文作成→応募実行→スプシ同期」）

以下を順番に実行する：
1. `SCRAPE_SKILL.md` → 上から20件チェック、キーワード一致する最大3件を収集
2. `DRAFT_SKILL.md` → 候補分の応募文を生成
3. `APPLY_SKILL.md` → フォーム送信
4. `python sync_sheets.py` → スプシに反映

### 個別実行

| 指示 | 実行内容 |
|------|---------|
| 「スクレイピングを実行」 | `SCRAPE_SKILL.md` |
| 「応募文を作成」 | `DRAFT_SKILL.md` |
| 「応募を実行」 | `APPLY_SKILL.md` |
| 「スプシ同期」 | `python sync_sheets.py` |

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
Phase 1: SCRAPE（20件チェック→最大3件）
  └→ inbox/{site}_{timestamp}_candidates.jsonl

Phase 2: DRAFT（候補分の応募文を生成）
  └→ inbox/{site}_{timestamp}_drafts.jsonl

Phase 3: APPLY（応募文をフォーム送信）
  ├→ inbox/{site}_{timestamp}_applied.jsonl
  └→ applied_urls.txt に追記（1件ごと即時）

Phase 4: SYNC
  ├→ applied.jsonl をスプシに反映（python sync_sheets.py）
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

- 毎日回す前提 → 上から20件チェック、条件一致3件で十分
- 3件収集→3件生成→3件応募（無駄ゼロ）
- 直列実行でバトンファイル待ちの空白時間なし
- Chrome MCPでDOM直接操作（Computer Useより高速・軽量）

---

## 注意事項

- 各サイトには事前にブラウザでログインしておくこと
- PCの電源が入っている必要がある（ローカル実行のため）
- candidates.jsonl と drafts.jsonl は sync_sheets.py の処理対象外（action が "candidate" / "draft" のためスキップ）
- **ファイル書き込みにBashのechoは使わない**（日本語文字化け防止）。Write/Editツールを使うこと
