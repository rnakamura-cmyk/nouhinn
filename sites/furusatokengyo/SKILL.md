# ふるさと兼業 応募手順

## サイト情報
- URL: https://furusatokengyo.jp/
- ログイン: ブラウザで事前にログイン済みであること
- 特徴: 地方企業の副業・兼業マッチング。報酬よりも関わりの深さ・地域貢献文脈の案件が多い

---

## 検索手順

> ✅ 確認済み（2026-04-01）：検索URL構造・フィルター名を実機で確認済み。

`config.json` の `search_filters` を参照して以下の手順で操作する。

### 1. 案件一覧ページにアクセス
- **検索ベースURL**: `https://furusatokengyo.jp/project/case/search/typeA2`
- ホームページの「プロジェクトを探す」リンクから同URLに遷移可能

### 2. 検索パラメータ
フォームはGETパラメータで検索できる。主なパラメータ名：

| パラメータ | 説明 | 例 |
|-----------|------|-----|
| `mase_case_search_type_a2[caseKeyword]` | キーワード | DX, AI, 自動化 |
| `mase_case_search_type_a2[caseItemCodeVarchar01]` | エリア | GN030003（関東） |
| `mase_case_search_type_a2[caseItemCodeVarchar02][]` | 職種別カテゴリ（複数可） | GN018（IT・エンジニア）, GN010（新規事業） |
| `mase_case_search_type_a2[caseItemCodeVarchar03][]` | テーマ別カテゴリ（複数可） | GN001（DX）, GN011（IT・テクノロジー） |
| `mase_case_search_type_a2[caseItemCodeVarchar04][]` | 関わり方（複数可） | GN001（業務委託）, GN006（リモート） |
| `mase_case_search_type_a2[sortType]` | 並順 | case_created_at |

**職種別カテゴリ（caseItemCodeVarchar02）主要コード:**
- GN018: IT・エンジニア
- GN019: WEBサービス
- GN020: アプリ開発
- GN010: 新規事業
- GN002: リサーチ・コンサルティング

**テーマ別カテゴリ（caseItemCodeVarchar03）主要コード:**
- GN001: DX
- GN011: IT・テクノロジー
- GN008: ソーシャルビジネス

**注意**: キーワード絞り込みは本文一致で動作。「IT」「DX」単体では合致案件が少ない可能性あり。キーワードなしで全件取得し、タイトル・カテゴリで手動フィルタリングが有効。

### 3. 案件を収集
- 絞り込みなしで全件（通常5〜20件程度と少ない）を取得して目視フィルタリング
- 各案件詳細ページURL形式: `/project/case/info/{案件ID}`
- COWORK_SKILL.md Step 3 の基準でフィルタリング
- 「移住可」「週3日以上」の案件は実質現地対応の場合が多い → 確認が必要
- 「移住×起業」「地域おこし協力隊」は実質移住必須のことが多い → NG

---

## 応募フォームの埋め方

> ✅ 確認済み（2026-04-02）：実フォームで全フィールドを確認・応募完了済み。
> フォームURL形式: `/project/case/entry/{案件ID}`
> 送信フロー: 申し込みボタン → 入力フォーム → 確認ボタン → 入力確認画面 → 登録ボタン → 申込完了

**フォームは通常のHTML form（React非使用）。通常の `.value` セットと `.dispatchEvent(new Event('change'))` で動作する。**

### フィールド一覧（確認済み）

| # | フィールド名 | name属性 | 必須/任意 | 種類 | 入力内容 |
|---|-----------|---------|---------|------|--------|
| 1 | 名前 | itemStrVarchar01 | 必須 | text | プロフィールから自動入力済み |
| 2 | ふりがな | itemStrVarchar02 | 必須 | text | 自動入力済み |
| 3 | 性別 | itemStrText19 | 必須 | select | M=男性, F=女性, O=その他, N=無回答 |
| 4 | 生年月日 | itemDatetime01 (year/month/day) | 任意 | select×3 | |
| 5 | 電話番号 | itemStrVarchar03 | 必須 | text | |
| 6 | メールアドレス | itemStrVarchar04 | 必須 | text | |
| 7 | 適格請求書発行事業者登録番号 | itemStrVarchar05 | 任意 | text | |
| 8 | お住まいの都道府県 | itemStrText20 | 必須 | select | 13=東京都 等 |
| 9 | 住所（市町村） | itemStrVarchar06 | 必須 | text | |
| 10 | 職歴①属性 | itemStrText08 | 必須 | select | GN0001=フリーランス, GN0002=個人事業主, GN0003=経営者 等 |
| 11 | 職歴①入社年月 | itemDatetime02 (year/month/day) | 任意 | select×3 | |
| 12 | 職歴①退職年月 | itemDatetime03 (year/month/day) | 任意 | select×3 | |
| 13 | 職歴①企業名 | itemStrVarchar07 | 任意 | text | |
| 14 | 職歴①部署名 | itemStrVarchar08 | 必須 | text | 「AXフリーランス（個人事業）」等 |
| 15 | 職歴①ポジション | itemStrVarchar09 | 任意 | text | |
| 16 | 職歴①業種 | itemStrVarchar14, itemStrVarchar15 | 必須 | select×2 | GN010007=IT・インターネット 等 |
| 17 | 職歴①職種 | itemStrVarchar16, itemStrVarchar17 | 必須 | select×2 | GN020010=IT技術職 等 |
| 18 | 職歴①フリーコメント | itemStrText01 | 任意 | textarea | |
| 19 | 経験ある業種①②③ | itemStrVarchar18-19, itemStrText09-12 | ①必須 | select×2(各) | |
| 20 | 得意な職種①②③ | itemStrText13-18 | 任意 | select×2(各) | |
| 21 | これまでの経歴 | itemStrText02 | 任意 | textarea | |
| 22 | 自己紹介・PR | itemStrText03 | 任意 | textarea | my_profile.md の実績を引用 |
| 23 | 外部サービス・サイト | itemStrText04 | 任意 | textarea | |
| 24 | **志望動機** | **itemStrText05** | **必須** | **textarea** | **応募文を入れるメインフィールド。地域貢献の文脈を添えると効果的** |
| 25 | 希望する契約形態 | itemStrVarchar10[] | 必須 | checkbox | GN0001=業務委託（副業兼業）, GN0002=雇用（時短）, GN0003=お試し転職, GN0004=プロボノ, GN0005=インターン |
| 26 | 参画可能な体制・条件 | itemStrVarchar11[] | 必須 | checkbox | GN0001=リモート対応, GN0002=現地対応, GN0003=移住可能, GN0004=早朝対応可, GN0005=夜間対応可, GN0006=日中対応可, GN0007=数日程度の短期間, GN0008=1ヶ月〜6ヶ月程度, GN0009=6ヶ月以上可 |
| 27 | 対応可能な時間数 | itemStrVarchar12[] | 必須 | checkbox | GN0001=スキマ時間(週8時間未満), GN0002=週1日程度, GN0003=週2日程度, GN0004=週3日以上 |
| 28 | 面談可能な日程 | itemStrText06 | 必須 | textarea | 「平日日中であればいつでも対応可能」等 |
| 29 | 備考・ご要望など | itemStrText07 | 任意 | textarea | |

### name属性のプレフィックス
全フィールドのname属性は `mase_case_entry_type_a2[...]` の形式。例：`mase_case_entry_type_a2[itemStrText05]`

### 注意事項
- 添付ファイル欄は**なし**
- プロフィール情報（名前・ふりがな・都道府県）はマイページ設定から自動入力される
- 電話番号は必須だが自動入力されない → 毎回入力が必要
- checkboxは `.checked = true` で選択可能（React非使用のため通常DOM操作でOK）

---

## 出力ファイル名
`furusatokengyo_YYYYMMDD_HHMMSS.jsonl`

## 備考
- ログイン状態が切れている場合は先にログインしてから再実行すること
- ふるさと兼業は「なぜこの地域・この会社に興味を持ったか」を応募文に入れると通過率が上がる傾向がある
- フォーム構造が変わっていた場合は、このファイルの「応募フォームの埋め方」を更新すること
