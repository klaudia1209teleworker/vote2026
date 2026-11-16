# 追蹤

## 狀態（2026-11-16）

全站直連 GA4，Measurement ID：`G-NNCFK0YYDC`。

這是相對共用 GTM 規則的例外：沒有 GTM 容器，頁面只載入一份 `gtag.js`。裁決見 [`.cursor/rules/project/000-project-authority.mdc`](../rules/project/000-project-authority.mdc)。

- ID 常數：`src/constants/analytics.ts`
- 載入位置：`src/layouts/Layout.astro` 的 `<head>`，所有公開頁共用
- 不延遲到 `window.load`
- 不掛同意橫幅
- 目前沒有自訂事件
