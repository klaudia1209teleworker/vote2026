# Cursor Project Rules（跨專案共用）

本目錄為 **`.cursor/rules/`**，存放 Cursor **Project Rules**（以 `.mdc` 為主）。**整體架構**（`rules`／`prd`／`design-input` 分工）請先看 **[`../README.md`](../README.md)**。

**Claude Design 三件套**集中在子資料夾 **`claude-design/`**（與編號規則分開）。不需要此流程的專案，複製規則時可**不要複製**該資料夾，或複製後**整包刪除** `.cursor/rules/claude-design/` 即可，不影響其餘 `.mdc`。

**設計稿目錄**：`design-input/` 位於**專案根目錄**（與 `.cursor/` 同層），說明見倉庫根 [design-input/README.md](../../design-input/README.md)。

**專案 PRD**：寫在 **`.cursor/prd/`**，使用方式與建議檔案結構見 [prd/README.md](../prd/README.md)。

---

## 快速上手：`ci.mdc` 與 Claude Design HTML

### 更新 `ci.mdc` 之後

| 步驟 | 說明 |
|------|------|
| 編輯位置 | 目標專案：`.cursor/rules/claude-design/ci.mdc`（每專案一份，填實際色票／字型／資產路徑）。 |
| 生效方式 | 存檔即可；Cursor 依 `alwaysApply`／`globs` 於後續對話載入新版本。 |
| 與程式對齊 | 變更 token 時請**同一輪變更**同步 `tailwind.config`（或 CSS 變數），避免規則與 build 不一致。 |
| 多客戶複用 | 若使用本機 CI 庫：在庫內改好後，複製覆蓋該專案的 `claude-design/ci.mdc`。 |
| 本倉庫範本 | `claude-design/ci.mdc` 為**範本**；真實客戶 CI 建議留在各專案 repo，除非你們政策允許集中版控。 |

`_handoff` 轉檔時會對照**當下** `ci.mdc` 做色彩映射；輸出目錄對齊**目標專案技術棧**（見 `_handoff.mdc`）。三件套內部優先序 **`ci` > `_handoff` > `_stack`**。`_stack` 為 Next.js **注意事項**，非預設棧。

### 掛載 Claude Design 產出的 HTML

HTML 不作為正式路由頁「掛」進 Next，而是當**轉元件的輸入**，固定放在專案根目錄的 `design-input/`（與 `_handoff.mdc` 的 `globs` 一致）。

| 情境 | 建議路徑 |
|------|----------|
| 單一匯出檔 | `design-input/landing.html`（檔名自訂） |
| ZIP 解壓 | `design-input/專案或頁面名/index.html`（及隨附 css/js／圖片） |
| 多頁原型 | 每個 HTML 對應專案既有路由下的一頁（Next App Router 才是 `src/app/.../page.tsx`） |

**在 Cursor 裡操作**：開啟該專案，確認存在 `.cursor/rules/claude-design/`（內含 `_handoff.mdc`、`ci.mdc`；Next 專案才會用到 `_stack.mdc`）。於 **Composer** 下指令，並可 `@` 指到規則檔，例如：

- 「請依 `_handoff` 規則，將 `design-input/landing.html` 轉成元件與頁面；**輸出對齊本專案既有目錄**；色彩對照 `ci.mdc` 並輸出映射表。」
- 「`design-input/prototype/` 內有多個 HTML，請拆共用元件、建立對應路由，並列出尚未確認的 TODO。」

**版控**：`design-input/` 可納入 Git 或列入 `.gitignore`（整包忽略或僅忽略 ZIP 等）；詳見 **`claude-design/_handoff.mdc`** 內「`design-input/` 與版控（Git）」一節。

---

## 規則檔案結構（目前）

```
.cursor/rules/
├── README.md                           # 本說明
│
├── claude-design/                      # 可選：Claude Design 轉檔（不需要可不複製）
│   ├── README.md                       # 本套件說明（非 .mdc 規則）
│   ├── _handoff.mdc                    # HTML／ZIP 轉元件流程（不含品牌色）
│   ├── _stack.mdc                      # Next.js 注意事項（僅 Next 專案 globs；非 alwaysApply）
│   └── ci.mdc                          # 專案 CI token／字型（複製到目標專案後務必填寫）
│
├── # 核心流程
├── 000-core-workflow.mdc             # 核心開發流程（最高優先級）
├── 003-ui-design-delegation.mdc      # 任務委派：高門檻才開；GPT／Claude 各最多一次；程式留主代理
├── 049-agents-md.mdc                 # AGENTS.md 與 .cursor/rules／CLAUDE.md 分工
├── 050-claude-design-rules.mdc       # Claude Design / starter 規則掛載與優先順序
├── 001-deployment.mdc                # 部署前置作業（Web）
├── 002-app-development.mdc           # APP 開發驗證（模擬器 → 真機 → releases/ios/、semver + ios.buildNumber）
│
├── # TypeScript／React／後端注意事項（不指定預設棧）
├── 100-typescript-react.mdc          # TypeScript 與 React 規範
├── 101-firebase.mdc                  # Firebase 規範
├── 102-agentation-devtool.mdc        # Agentation 開發工具
│
├── # 效能
├── 200-performance-assets.mdc         # 效能優化（圖片、字體、懶加載、多語系與各地快取）
├── 201-css-optimization.mdc         # CSS 優化
├── 202-javascript-optimization.mdc    # JavaScript 優化
│
├── # SEO
├── 300-seo-basics.mdc                 # SEO 基礎規範
├── 301-schema-org.mdc                # Schema.org 結構化數據
├── 302-sitemap-robots.mdc            # Sitemap、robots.txt、llms.txt（訓練／檢索爬蟲分流）
├── 303-rendering-seo-visibility.mdc   # 渲染架構與 SEO 可見性
├── 304-generative-search-optimization.mdc  # GEO／GSO：實體圖、頁型 Schema、可摘錄內容
├── 305-consent-mode.mdc               # Consent Mode v2（GTM／dataLayer／同意橫幅；僅未登入公開頁）
├── 306-ga4-datalayer-events.mdc       # GA4 事件 dataLayer.push（格式／GTM／範例／TS 封裝）
├── 307-gtm-container.mdc              # 網站預設埋設 GTM Container（單一入口／識別碼／片段）
│
└── # 開發流程
    ├── 400-git-commit.mdc            # Git Commit、推送 GitHub 與日期制 Release Note
    └── 401-testing.mdc               # 測試規範（Vite 新專案 Vitest；既有 Jest 不強制遷移）
```

---

## Claude Design 交接三件套（路徑：`claude-design/`）

| 檔案 | 角色 | 跨專案共用 | 觸發／套用 |
|------|------|:----------:|------------|
| `claude-design/_handoff.mdc` | 轉換引擎（步驟、映射表、無障礙）；輸出對齊專案目錄 | ✅ | **僅** `design-input/**/*`（改元件時不自動載入） |
| `claude-design/_stack.mdc` | Next.js 注意事項（14／15／16 陷阱） | ✅ | **非** alwaysApply；`next.config.*`、`src/app/**`、`proxy.ts`／`middleware.ts` |
| `claude-design/ci.mdc` | 品牌色票與 Tailwind token | ❌（每專案填寫） | 範本 `alwaysApply: false`；**填完色票後**改 `true` |

三檔內文仍稱彼此為「同目錄下的 `ci.mdc`」等，係指**同一資料夾 `claude-design/`** 內相對路徑，無需改檔名。

**衝突時優先順序**：`ci.mdc` > `_handoff.mdc` > `_stack.mdc`（皆指 `claude-design/` 內檔案）。

**與編號規則並用時**：**技術棧以目標專案為準**，共用規則只提供注意事項。`100` 不指定 Vite；`_stack` 只在 Next 專案載入。不需要 Claude Design 時移除整個 `claude-design/`。

設計稿放置、更新 CI 與 Composer 範例請見上文 **「快速上手」**。

---

## Claude Design / cursor-rules-starter（050 規則）

本倉庫實際掛載為 **`claude-design/` 子資料夾**（見 `050-claude-design-rules.mdc`）。**不要**再把檔案改名成根目錄 `051`–`053`。不需要此流程則不要複製該資料夾。

## 編號規則（000–499）

| 編號範圍 | 類別 |
|----------|------|
| 000-099 | 核心流程規範（最高優先級） |
| 001 | Web 部署前置作業 |
| 002 | APP 開發驗證（Dev Client、`releases/ios/`、semver + `ios.buildNumber`、Git tag） |
| 003 | 任務委派：僅新畫面／新流程／可見行為或權限變更才開；介面與文案給 GPT（`gpt-5.6-sol-medium`）、規格抓漏給 Claude（`claude-opus-5-5-medium`），各最多一次；禁止探索用 Task；程式留主代理 |
| 049 | AGENTS.md 與 `.cursor/rules`／`CLAUDE.md` 整合（跨工具總則；編號避開 051–053） |
| 050 | 外部規則整合（Claude Design / `cursor-rules-starter` 掛載與優先順序） |
| 100-199 | 各技術注意事項（TypeScript／React、Firebase；**不**指定預設棧） |
| 200-299 | 效能優化規範 |
| 300-399 | SEO、內容與同意／隱私規範 |
| 400-499 | 開發流程規範（Git, Testing） |

---

## 規則 metadata 與套用方式

每個 `.mdc` 檔案可包含：

```yaml
---
description: 規則描述
globs:
  - "**/*.ts"
alwaysApply: false
---
```

| 類型 | 說明 |
|------|------|
| `alwaysApply: true` | 每次對話載入（如 `000`、`003`、`049`、`050`、`400`）。**不要**把未填的 `ci.mdc` 或 Next 專用 `_stack` 設為 true |
| `globs` 匹配 | 編輯符合路徑的檔案時自動載入 |
| 手動引用 | 在對話中使用 `@檔名` 或 `@.cursor/rules/claude-design/_handoff.mdc`（以 Rules 面板顯示為準） |

---

## 變更紀錄（近期）

| 日期 | 檔案 | 變更摘要 |
|------|------|----------|
| 2026-10-19 | `003`、`000`、`AGENTS.md` | 收緊子代理：僅新畫面／新流程／可見行為或權限變更才主動開；同一件事 Claude／GPT 各最多一次；禁止探索用 Task |
| 2026-10-18 | `003`、`000`、`AGENTS.md`、`.cursor/README.md`、`SYNC-CURSOR-RULES.md` | `003` 收成總委派：介面與文案給 GPT、規格抓漏給 Claude Opus（阻擋最多 3 題）、程式留主代理；檔名不改 |
| 2026-10-18 | `003`、`000`、`AGENTS.md` | 介面／版面／視覺／元件設計委派子代理；呼叫時指定 `gpt-5.6-sol-medium`；`.cursor/agents/` 只定角色與流程，sync 不同步 |
| 2026-09-28 | `304`、`301`、`300`、`AGENTS.md` | 依反轉運輸 GEO：同一頁實體圖、`LocalBusiness` 僅靜態頁、頁型 Schema、Schema 只寫可見內容；`301` 的商家 `@id` 與 `publisher` 對齊 |
| 2026-08-28 | 多檔 | 收斂 GTM 載入順序；commit／push 須用戶要求；`400` alwaysApply；og:image 依專案；handoff 僅 design-input glob；Android／PurgeCSS／爬蟲 UA 等 |
| 2026-08-28 | `000`、`049`、`050`、`100`、`_stack`、`ci`、`AGENTS.md` 等 | **技術棧以各專案為準**：共用規則改為各技術注意事項；`_stack`／未填 `ci` 取消 alwaysApply；廢棄 051–053 掛載建議 |
| 2026-08-28 | `401-testing.mdc`、`100-typescript-react.mdc`、根目錄 `AGENTS.md` | 測試工具跟隨專案；Vite 新開測試可優先 Vitest；既有 Jest 不強制遷移 |
| 2026-08-28 | `049-agents-md.mdc`、根目錄 `AGENTS.md` | 新增 AGENTS.md 與 `.mdc` 分工／優先序；`CLAUDE.md` 為 `AGENTS.md` symlink；sync 腳本仍不同步 `AGENTS.md` |
| 2026-08-28 | `000-core-workflow.mdc`、`050-claude-design-rules.mdc` | 交叉引用 049：衝突以 `.mdc` 為準，禁止與 `AGENTS.md` 雙寫完整規範 |
| 2026-08-28 | `302-sitemap-robots.mdc` | AI 爬蟲改為訓練用／即時檢索用分流：`ClaudeBot` 取代 `anthropic-ai`；即時檢索類必須放行；Bytespider 封鎖＋WAF；新增驗證清單 |
| 2026-08-28 | `304-generative-search-optimization.mdc`、`300-seo-basics.mdc` | 交叉引用 302：訓練／檢索爬蟲不可共用同一條規則 |
| 2026-08-28 | `claude-design/_stack.mdc` | 基準升級為 Next.js 16：Turbopack、`proxy.ts`、async 動態 API、Cache Components、`next lint` 移除；附 14／15 相容性表 |
| 2026-08-28 | `claude-design/_handoff.mdc`、`001-deployment.mdc`、`050` | 對齊 Next.js 16：轉檔 Server/Client 判斷、禁止依賴 `next lint`、接手舊版先詢問 |
| 2026-08-05 | `sync-cursor-rules.sh` | sync 明確 `--exclude=project/`；更新 SYNC-CURSOR-RULES 與儲存對照表 |
| 2026-08-05 | `../README.md` | 文件：補「規則儲存對照」（cursor-rules ↔ 應用專案；sync 覆寫範圍表） |
| 2026-08-05 | `../README.md`、`prd/README`、`SYNC-CURSOR-RULES` | 文件：共用／專案衝突時以 `project/` 裁決、共用檔 stub／降級、轉碼分拆、Sync 後檢查清單 |
| 2026-08-05 | `400-git-commit.mdc` | 新增：用戶要求推送／部署 push 後必須建立 GitHub Release；tag 採 `vYYYY.MM.DD`（同日 `-N`）；同步 000／001／002 |
| 2026-08-05 | `307-gtm-container.mdc` | 新增：網站預設必須埋設 GTM Container；單一入口、識別碼、標準片段；交叉引用 305／306／200 |
| 2026-08-05 | `306-ga4-datalayer-events.mdc` | 新增：GA4 事件 dataLayer.push 格式、GTM 變數／觸發／標籤、SPA／轉換範例、TS 封裝 |
| 2026-08-05 | `305-consent-mode.mdc` | 新增「GTM 與 GA4 dataLayer 處置」；實作前必問外部 CMP／自製與追蹤盤點；僅未登入公開頁；交叉引用 306／307 |
| 2026-08-05 | `200-performance-assets.mdc` | 新增 §5 多語系載入與各地快取（Vite／Next／通用 React；引用 101 Firebase headers） |
| 2026-08-05 | `302-sitemap-robots.mdc` | 新增 Sitemap XSLT：人看表格顯示 URL／lastmod／頻率／優先度；XML 保留 hreflang 給搜尋引擎 |

| 2026-06-17 | `300-seo-basics.mdc` | 同步 Meta Tags（無 og:image、twitter:summary）、首頁 H1、Canonical SPA 規範、GEO 實作要點與驗證清單 |
| 2026-06-17 | `302-sitemap-robots.mdc` | 同步 robots Disallow 衝突規則、AI 爬蟲設定、Firebase llms.txt／sitemap 生成流程與 `generate-seo` 整合腳本 |

---

## 使用與維護

1. **自動套用**：Cursor 依 `globs` 與 `alwaysApply` 載入規則。
2. **手動引用**：例如 `@000-core-workflow`，或 `@` 指向 `claude-design` 內規則檔路徑。
3. **本倉庫**：修改 `.mdc` 後提交並 push，作為各專案同步來源。
4. **各專案**：不需要 Claude Design 時，**不要複製** `claude-design/`。`_stack` 僅 Next 專案會被 globs 載入；`ci.mdc` 填完色票後再設 `alwaysApply: true`。
5. **與專案事實衝突時**：在目標專案用 `rules/project/` 裁決＋對共用檔 stub／降級；轉碼改走專案版 handoff。見 [../README.md](../README.md)「共用規則與專案規則衝突時」、[../../scripts/SYNC-CURSOR-RULES.md](../../scripts/SYNC-CURSOR-RULES.md) Sync 後檢查清單。

所有規則檔案建議納入版本控制。

---

## 參考資源

- [Cursor Rules 官方文檔](https://docs.cursor.com/context/rules)
- [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- [cursor.directory](https://cursor.directory/)
