# AGENTS.md

跨工具 AI 代理總則（Cursor、Claude Code、Aider、Zed 等皆讀本檔）。**細則只寫在** [`.cursor/rules/`](.cursor/rules/)；本檔只放摘要與索引。分工、衝突優先序、`CLAUDE.md` 作法見 [`049-agents-md.mdc`](.cursor/rules/049-agents-md.mdc)。

---

## 專案基本資訊

| 項目 | 內容 |
|------|------|
| 專案名稱 | vote2026 |
| 類型 | Web（靜態站） |
| 主要語言 | TypeScript／Astro |
| 技術棧 | **以本專案為準**（讀 `package.json`／既有目錄）：Astro 7、Tailwind CSS 4（`@tailwindcss/vite`）、`output: 'static'`、部署至 GitHub Pages（`site` + `base: '/vote2026/'`） |

---

## 核心行為原則

1. **先讀規則再開工**。讀 `000` 與本次相關規則；Claude Design 僅在專案使用該流程時再讀 `050` 與 `claude-design/`。文件與程式衝突、需求模糊、架構決策：**先詢問再行動**。見 [`000-core-workflow.mdc`](.cursor/rules/000-core-workflow.mdc)。
2. **技術棧不由共用規則指定**。以本專案 `package.json`、既有架構、`rules/project/`（若有）為準；共用 `.mdc` 只提供各技術注意事項，禁止為了對齊規則而換框架。
3. **變更後同步文件**。程式／規則異動後更新對應 `.mdc`；若動到跨工具總則，只改本檔的**一句話摘要**（禁止與 `.mdc` 各寫一份完整規範）。
4. **衝突優先序**：專案事實／`project/` > `000-core-workflow.mdc` > 其餘已載入的注意事項 > 本檔。Claude Design 三件套內部：`ci.mdc` > `_handoff.mdc` > `_stack.mdc`。
5. **推送即發 Release**。用戶要求推送 GitHub、或部署含 `git push` 時，依 `400-git-commit.mdc` 建立日期制 GitHub Release（`vYYYY.MM.DD`）。

---

## 技術棧摘要

- 框架／bundler：Astro 7（Vite）
- 樣式：Tailwind CSS 4（`@tailwindcss/vite`）；全站黑白灰階 token，見 [`ci.mdc`](.cursor/rules/claude-design/ci.mdc) 與 [`ui-guideline.md`](.cursor/prd/ui-guideline.md)
- 後端／BaaS：無（靜態輸出）
- 部署環境：GitHub Pages（`https://klaudia1209teleworker.github.io/vote2026/`）

注意事項入口（有用到才看，不要為了規則改棧）：

- TypeScript／React 寫法：[`100-typescript-react.mdc`](.cursor/rules/100-typescript-react.mdc)（本專案以 Astro 為主；未引入 React 套件時勿假設必須用 React）

---

## Commit／測試／部署

- **Commit**：僅在用戶要求時執行；訊息與流程見 [`400-git-commit.mdc`](.cursor/rules/400-git-commit.mdc)。
- **測試**：跟隨專案既有工具；見 [`401-testing.mdc`](.cursor/rules/401-testing.mdc)。
- **Web 部署**：先清調適檔與無用測試頁，修復 ESLint 後再 build／push。見 [`001-deployment.mdc`](.cursor/rules/001-deployment.mdc)。

---

## Development（Astro）

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

---

## Documentation（Astro）

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

---

## 詳細規則索引

完整內容以各 `.mdc` 為準；本表只做入口。未使用的列已省略（含 APP、Firebase、Claude Design；若日後啟用再補回）。

| 規則 | 一句話 |
|------|--------|
| [`000-core-workflow.mdc`](.cursor/rules/000-core-workflow.mdc) | 核心流程：專案棧為準、先問再做、變更同步文件 |
| [`003-ui-design-delegation.mdc`](.cursor/rules/003-ui-design-delegation.mdc) | 任務委派：高門檻才開；介面／文案給 GPT、規格抓漏給 Claude，各最多一次；程式留主代理 |
| [`001-deployment.mdc`](.cursor/rules/001-deployment.mdc) | Web 部署前置：清調適、修 ESLint、再 build |
| [`049-agents-md.mdc`](.cursor/rules/049-agents-md.mdc) | 本檔與 `.mdc`／`CLAUDE.md` 的分工與優先序 |
| [`100-typescript-react.mdc`](.cursor/rules/100-typescript-react.mdc) | TypeScript／React 寫作注意事項（不指定 bundler） |
| [`200-performance-assets.mdc`](.cursor/rules/200-performance-assets.mdc) | 圖片、字體、懶加載、多語系快取 |
| [`201-css-optimization.mdc`](.cursor/rules/201-css-optimization.mdc) | CSS 效能注意事項 |
| [`202-javascript-optimization.mdc`](.cursor/rules/202-javascript-optimization.mdc) | JavaScript 效能注意事項 |
| [`300-seo-basics.mdc`](.cursor/rules/300-seo-basics.mdc) | SEO 基礎（meta 依框架實作、H1、canonical） |
| [`301-schema-org.mdc`](.cursor/rules/301-schema-org.mdc) | Schema.org 結構化資料 |
| [`302-sitemap-robots.mdc`](.cursor/rules/302-sitemap-robots.mdc) | Sitemap、robots.txt、llms.txt；訓練／檢索爬蟲分流 |
| [`303-rendering-seo-visibility.mdc`](.cursor/rules/303-rendering-seo-visibility.mdc) | 渲染與 SEO；不為 SEO 擅自換棧 |
| [`304-generative-search-optimization.mdc`](.cursor/rules/304-generative-search-optimization.mdc) | GEO：可摘錄內容、實體圖 `@id`、頁型 Schema、只寫可見事實 |
| [`305-consent-mode.mdc`](.cursor/rules/305-consent-mode.mdc) | Consent Mode v2（僅未登入公開頁） |
| [`306-ga4-datalayer-events.mdc`](.cursor/rules/306-ga4-datalayer-events.mdc) | GA4 `dataLayer.push` 事件 |
| [`307-gtm-container.mdc`](.cursor/rules/307-gtm-container.mdc) | 公開站預設建議 GTM；例外記入專案；容器不可延遲載入 |
| [`400-git-commit.mdc`](.cursor/rules/400-git-commit.mdc) | Commit（僅用戶要求）；推送後日期制 GitHub Release |
| [`401-testing.mdc`](.cursor/rules/401-testing.mdc) | 測試注意事項（跟隨專案） |

規則清單與套用方式另見 [`.cursor/rules/README.md`](.cursor/rules/README.md)。

---

## 其他工具設定檔

- **`CLAUDE.md`**：若需要，應為本檔的 symlink（`ln -s AGENTS.md CLAUDE.md`）；無法使用 symlink 時改為一句指向說明。不要另寫一份完整規範。（目前尚未建立，待確認。）
- **`scripts/sync-cursor-rules.sh`**：同步 `.cursor/` 與 `design-input/README.md`，**不同步本檔**。跨專案共用段落異動時需手動對齊；專案專屬填空本來就不該被腳本覆蓋。
