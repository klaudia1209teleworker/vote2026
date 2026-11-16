# `design-input/` — Claude Design 匯入區

此資料夾位於**專案根目錄**（與 `src/`、`.cursor/` 同層），用來放 **Claude Design** 匯出的 HTML，或 ZIP 解壓後的內容，**不作為正式上線程式碼**，僅供依 Cursor 規則轉成 `src/` 元件前的輸入。與 `.cursor/rules`、`prd` 的整體關係見 **[`.cursor/README.md`](../.cursor/README.md)**。

## 新專案要怎麼做

1. 在**你的應用專案根目錄**建立同名資料夾：`design-input/`（若從本倉庫對照，結構與此處一致即可）。
2. 將設計匯出放入，例如：
   - `design-input/landing.html`
   - `design-input/某原型/index.html`（ZIP 解壓後整包放子資料夾）
3. 確認該專案已複製 **`.cursor/rules/claude-design/`**（含 `_handoff.mdc`），並已填寫 **`claude-design/ci.mdc`**。
4. 在 Cursor **Composer** 中下指令，例如：「依 `_handoff` 規則，將 `design-input/…` 轉成元件與頁面；**輸出路徑對齊本專案既有目錄**（不要假設一定是 `src/app/`）。」

詳細流程、色彩映射與 **Git／`.gitignore`** 建議見：

- [`.cursor/rules/claude-design/_handoff.mdc`](../.cursor/rules/claude-design/_handoff.mdc)
- [`.cursor/rules/README.md`](../.cursor/rules/README.md)（快速上手；規則索引）

## 關於本倉庫（cursor-rules）

本 repository 根目錄的 `design-input/` 為**範例位置**：方便複製目錄結構到新專案。實際 HTML／ZIP 可依團隊政策納入 Git 或僅放本機；本倉庫透過 `.gitignore` 預設**不追蹤**此目錄內除本 README 以外的檔案，避免大型匯出被誤提交。
