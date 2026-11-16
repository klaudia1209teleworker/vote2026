# `.cursor/prd/` — 專案 PRD 與規格文件

本資料夾只放**當前專案**的產品／交付文件（PRD、決策、里程碑等）。**不附任何範本業務檔**（如假 PRD）；團隊依下方結構自行新增 `.md` 即可。

---

## 與 `rules/` 有什麼不同？

| | `.cursor/rules/` | `.cursor/prd/` |
|---|------------------|----------------|
| 檔案型別 | 主要為 `.mdc`（Project Rules） | 一般 **`.md`** 文件 |
| Cursor 怎麼用 | 依設定**自動或條件載入**為規則 | **不**當規則索引；由你在對話或規則裡 **`@` 引用** |
| 內容長度 | 宜短、可執行 | 可長篇、可頻繁改版 |

總覽與分層理由見 **[`.cursor/README.md`](../README.md)**。

---

## 如何使用

1. **新增檔案**：在此目錄建立 `*.md`（檔名建議見下一節）。  
2. **在聊天引用**：輸入 `@.cursor/prd/你的檔名.md`，只載入本次討論需要的範圍。  
3. **在規則裡引用**：若專案有 `.cursor/rules/project/*.mdc`，可在內文寫「實作前請參考 @.cursor/prd/xxx.md」。  
4. **版控**：是否 commit 由專案決定；機敏 PRD 可只放本機（並列入 `.gitignore`）。

---

## 建議的 PRD 結構（怎麼建立才「好引用」）

讓 Agent 與人類都能快速對齊時，建議遵守：

### 檔名與粒度

- **一主題一檔**：例如 `product-prd.md`、`non-goals.md`、`api-contracts.md`，避免單檔過萬字難以 `@` 精準引用。  
- **可加前綴區分階段**：`v1-product-prd.md`、`2026-q2-roadmap.md`。  
- **子目錄（可選）**：若文件很多，可用 `prd/features/checkout.md`；引用時改為 `@.cursor/prd/features/checkout.md`（與實際路徑一致即可）。

### 單一 PRD 建議大綱（Markdown 標題）

```markdown
# [專案或功能名稱] PRD

## 背景與目標
## 使用者／場景
## 功能範圍（In scope）
## 非目標（Out of scope）
## 使用者故事或流程
## 驗收標準
## 開放議題與風險
## 修訂紀錄（日期、作者、摘要）
```

- **驗收標準**寫成可勾選項目，有利 Agent 對照實作。  
- **修訂紀錄**避免只覆寫舊段而不留痕，減少與程式現況脫節。

### 與 Rules 的邊界

- **商業邏輯、優先級、取捨** → 寫在 `prd/`。  
- **程式風格、架構硬性規定** → 寫在 `rules/`（`.mdc`），必要時在 `.mdc` 內 `@` 連到 `prd/` 對應段落。

---

## `@` 引用範例

- `@.cursor/prd/product-prd.md`  
- `@.cursor/prd/features/auth.md`

（路徑一律相對於**專案根目錄**。）

---

## 可選：`rules/project/` 與本目錄的搭配

若希望「規則區」也有一個專案入口檔，可新增（本倉庫未預建，由專案自建）：

```
.cursor/
├── rules/
│   └── project/
│       ├── 000-project-authority.mdc  # 建議：alwaysApply；衝突裁決＋專案事實
│       ├── 050-…-stack.mdc            # 可選：僅當要寫下「本專案技術棧事實」時（共用規則已不指定棧）
│       ├── 051-design-handoff.mdc     # 可選：專案轉碼流程（當共用 _handoff 不符時）
│       └── （其他短規則；可 @ 連結 prd）
└── prd/
    └── README.md                     # 本說明
    └── （團隊自建的 *.md）
```

長篇仍放在 **`prd/`**；`project/*.mdc` 只負責索引、硬性專案慣例與**衝突裁決**。架構總覽見 [`.cursor/README.md`](../README.md)。

---

## 衝突裁決與 stub（與共用規則並存時）

專案決策紀錄（非上游範本）：

- [candidate-performance-display.md](./candidate-performance-display.md) — 候選人頁政見、出席率／質詢／提案指標與明細顯示
- [ui-guideline.md](./ui-guideline.md) — 全站黑白灰階 UI；不改資料、不加開票頁或示意地圖
- [candidate-city-index.md](./candidate-city-index.md) — 候選人總覽與縣市頁如何進入各職位名單
- [ballot-lookup.md](./ballot-lookup.md) — 首頁選票查詢的村里選填，以及村里長名單如何只顯示一里
- [analytics.md](./analytics.md) — 全站直連 GA4 `G-NNCFK0YYDC`，不接 GTM、不掛同意橫幅

當上游注意事項與專案現況衝突（例如 `_handoff` 路徑、305／307 的 GTM vs 專案已直連 gtag）時：

| 步驟 | 位置 | 做什麼 |
|------|------|--------|
| 1. 裁決 | `rules/project/000-project-authority.mdc`（`alwaysApply: true`） | 列專案事實；聲明衝突時以 `project/` 為準 |
| 2. 降級 | 目標專案內易衝突的**共用** `.mdc` | 改 stub：`alwaysApply: false`、`globs: []`、短文指向 `project/…` |
| 3. 轉碼 | `rules/project/051-design-handoff.mdc`（檔名可自訂） | 專案版 design → 程式流程；並 stub 共用 `_handoff` |
| 4. 長文 | `prd/*.md` | 產品／決策細節；由 authority 或專案規則 `@` 引用 |

**常見需 stub 的共用檔**：`claude-design/_handoff.mdc`、`305-consent-mode.mdc`、`307-gtm-container.mdc`（僅當專案已文件化的追蹤方案與注意事項仍衝突時）。`_stack.mdc` 僅 Next 專案 globs 載入，Vite 專案通常不必 stub。

**Sync 注意**：`project/**` 與 `prd/` 業務 `.md` **不會**被 `sync-cursor-rules.sh` 覆寫；共用 stub **會**被上游還原。每次 sync 後請依 [scripts/SYNC-CURSOR-RULES.md](../../scripts/SYNC-CURSOR-RULES.md) 的檢查清單重新降級。
