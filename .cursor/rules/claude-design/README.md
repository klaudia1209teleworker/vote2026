# `claude-design/` — Claude Design 交接規則（選用）

本資料夾內為 **Cursor Project Rules**（`.mdc`），用於把 Claude Design 匯出的 HTML／ZIP 轉成專案元件。**不指定**目標專案必須使用 Next.js。

| 檔案 | 用途 |
|------|------|
| `_handoff.mdc` | 轉換流程；**輸出路徑對齊專案既有目錄**（Next App Router／Pages／Vite SPA） |
| `_stack.mdc` | **Next.js 注意事項**（僅當專案使用 Next.js 時由 globs 載入；14／15／16 見該檔相容表） |
| `ci.mdc` | **專案填寫**：色票、字型、Tailwind token。範本 `alwaysApply: false`；填完後改 `true` |

**不需要此流程的專案**：刪除整個 `claude-design/` 資料夾即可。

**設計稿放置**：專案根目錄的 `design-input/`（見倉庫根 `design-input/README.md`）。

**整體架構與 PRD 分層**：見 [`.cursor/README.md`](../../README.md) 與 [`../README.md`](../README.md)。跨工具總則見倉庫根 `AGENTS.md`（見 `049-agents-md.mdc`）。技術棧以目標專案為準（見 `000-core-workflow.mdc`）。
