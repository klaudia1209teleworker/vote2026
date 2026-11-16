# `.cursor/` 目錄總覽

本檔說明 **`.cursor/`** 底下各資料夾的分工與專案根目錄上與 Cursor 協作相關的路徑，方便新專案對照建立目錄。細節請再讀各子資料夾的 README。

---

## 架構一覽

單一**應用專案**根目錄內的路徑：

```
專案根目錄/
├── AGENTS.md                  # 跨工具 AI 總則（摘要；sync 不同步）
├── CLAUDE.md                  # 建議為 AGENTS.md 的 symlink（或一句指標檔）
├── design-input/              # 設計稿匯入（不在 .cursor 內；見該資料夾 README）
├── .cursor/
│   ├── README.md              # 本檔：整體架構
│   ├── rules/                 # Cursor Project Rules（.mdc，Agent 行為規範）
│   │   ├── README.md        # 規則索引、編號、metadata、Claude Design 說明
│   │   ├── *.mdc            # 共用規則（自 cursor-rules 同步）
│   │   ├── project/         # 可選：專案專屬規則（不同步覆寫）
│   │   └── claude-design/   # 可選：Claude Design 三件套
│   ├── prd/                   # 專案 PRD／規格（Markdown 文件，非規則引擎）
│   │   └── README.md        # PRD 怎麼用、建議目錄與撰寫結構
│   └── agents/                # 可選：專案子代理（只定角色與流程；模型由 003 呼叫時指定）
│       └── *.md             # 例：介面／文案、規格抓漏。sync 不複製、不覆寫
```

---

## 規則儲存對照（共用來源 ↔ 應用專案）

Cursor **只讀當前專案根**的 `.cursor/rules/`；本倉庫是跨專案的**單一來源**，需用 sync／複製掛進各應用專案。根目錄 **`AGENTS.md`** 為跨工具摘要，**不**由 `sync-cursor-rules.sh` 複製（見 [`049-agents-md.mdc`](rules/049-agents-md.mdc)）。

```
cursor-rules 倉庫（共用來源）
└── .cursor/rules/*.mdc          → 用 sync 複製到各專案
    （含編號規則、claude-design/ 範本等）

應用專案
├── AGENTS.md / CLAUDE.md        ← 跨工具總則（**不同步**；各專案填空）
├── .cursor/
│   ├── rules/                   ← 共用規則（從上游同步）
│   │   ├── 000-….mdc
│   │   ├── claude-design/ci.mdc ← 專案填寫（sync 預設不覆寫既有檔）
│   │   └── project/*.mdc        ← 專案規則（可選，不同步覆寫）
│   └── prd/*.md                 ← 專案 PRD（不同步覆寫；僅同步 prd/README.md）
└── design-input/                ← 設計稿輸入（專案根；說明檔可被 sync）
```

| 路徑 | 誰維護 | Sync 行為 |
|------|--------|-----------|
| `rules/` 編號規則、`claude-design/_stack`／`_handoff` 等 | 上游 cursor-rules | **會覆寫**同名檔（含你改過的 stub） |
| `rules/claude-design/ci.mdc` | 各專案填色票 | 目標已存在則**預設跳過**（`--force-ci` 才覆寫） |
| `rules/project/**` | 各專案 | **不同步**（腳本 `--exclude='project/'`；不會寫入／覆寫） |
| `prd/*.md`（除 README） | 各專案 | **不複製、不刪除** |
| `prd/README.md`、`.cursor/README.md` | 上游說明 | **會更新**說明檔 |
| 根目錄 `AGENTS.md`／`CLAUDE.md` | 各專案填空（技術棧等） | **不同步**；共用段落異動須手動對齊 |
| `.cursor/agents/**` | 各專案（角色、流程、原則） | **不同步**；介面／文案與規格抓漏的模型都由 `003` 在呼叫時指定，不寫進子代理檔 |

同步步驟見 [scripts/SYNC-CURSOR-RULES.md](../scripts/SYNC-CURSOR-RULES.md)。

---

## `rules/` 與 `prd/` 的分工

| 內容 | 位置 | 說明 |
|------|------|------|
| 跨工具總則（摘要、500–2,000 字） | 專案根 `AGENTS.md` | Cursor／Claude Code／Aider 等皆讀；細則禁止與 `.mdc` 雙寫（見 `049-agents-md.mdc`） |
| 可重用、要 Agent **遵守**的短規範 | `.cursor/rules/`（`.mdc` + frontmatter） | 由 Cursor 依 `globs`／`alwaysApply` 載入為 **Project Rules** |
| **專案專屬** PRD、決策、長篇規格、迭代紀錄 | `.cursor/prd/*.md` | 一般 Markdown；**不**當規則檔索引；以 `@.cursor/prd/…` **按需引用** |
| 專案內幾條硬慣例、又需連到長文 | 可選：`.cursor/rules/project/*.mdc`（精簡） | 內文用 `@` 指向 `prd/`；衝突時見下節 |

**不建議**在 `.cursor/rules/` 下再開 `prd/` 並堆長篇 `.md`：與通用 `.mdc` 混在同一規則樹，列表與載入語意都容易混亂。長文集中 **`prd/`**；若需要「規則目錄裡也有專案入口」，使用 **`rules/project/`** 內短 `.mdc` 即可。

---

## 共用規則與專案規則衝突時

上游共用規則是**各技術注意事項**，不指定專案必須用 Next 或 Vite。仍可能與**既有專案事實**衝突（例如 `_handoff` 路徑、Consent／GTM 與專案已直連 gtag）。處理原則：

### 1. 專案裁決檔（建議）

在目標專案新增 **`rules/project/000-project-authority.mdc`**（`alwaysApply: true`）：

- 明列本專案不可被規則「糾正」的事實（**技術棧**、目錄、分析／Consent 實作等）。
- 寫明：**與任何共用／上游規則牴觸時，以本檔與 `project/` 其餘規則為準**。
- **不得**為遷就共用規則而改動現有架構或技術選型。

細節與建議檔名見 [prd/README.md](prd/README.md)「衝突裁決與 stub」。

### 2. 易衝突共用檔：stub／降級（勿刪檔名）

對會誤導 Agent 的共用 `.mdc`，在**目標專案**改成 stub（保留路徑，避免 sync 後「檔案消失」造成混亂）：

| 做法 | 說明 |
|------|------|
| `alwaysApply: false` | 取消永遠載入 |
| `globs: []`（或極窄） | 避免編輯時自動掛上 |
| 內文改為短 stub | 說明「已降級」、指向 `project/…` 正確規則；必要時註明上游原文可手動 `@` |

常見需降級對象（依專案差異選用，非全部必做）：

| 共用檔 | 典型衝突 |
|--------|----------|
| `claude-design/_handoff.mdc` | 轉碼輸出路徑與專案目錄不符 |
| `050-claude-design-rules.mdc` | 僅在完全不用 Claude Design 且內容仍造成干擾時 |
| `305-consent-mode.mdc`、`307-gtm-container.mdc` | 專案已直連 gtag／其他 CMP，且已記入例外 |

`_stack.mdc` 已改為 **僅 Next.js 檔案觸發**（非 alwaysApply）。Vite／Expo 專案通常不必 stub；若 globs 仍誤觸再降級。

**`project/**` 不會被 sync 覆寫**；上述共用 stub **會**在下次 sync 被上游還原 → 必須依 [SYNC-CURSOR-RULES.md](../scripts/SYNC-CURSOR-RULES.md) 的 **Sync 後檢查清單**再降級一次。

### 3. 轉碼（design handoff）也要分開處理

若共用 `_handoff.mdc` 的目錄／棧假設不適用：

1. 將共用 `_handoff.mdc` **降級為 stub**（同上）。
2. 在 **`rules/project/`** 新增專案版 handoff（例如 `051-design-handoff.mdc`），`globs` 對準本專案的 `design-input/` 與實際元件路徑。
3. 轉碼流程、輸出目錄、CI 對照一律以 `project/` 該檔 + `ci.mdc` 為準。

### 4. 優先順序（應用專案內）

1. **專案事實**：`package.json`、既有架構、**`project/`**（含 `000-project-authority.mdc`）  
2. **`000-core-workflow.mdc`**  
3. 專案已填的 **`claude-design/ci.mdc`**（品牌 token；填完後才 alwaysApply）  
4. 其餘依 globs 載入的注意事項（編號規則、`_stack` 僅 Next、`_handoff` 僅轉檔）  
5. **`AGENTS.md`**：跨工具摘要；衝突時以專案事實與 `.mdc` 為準（見 `049-agents-md.mdc`）

---

## `design-input/`（專案根目錄）

Claude Design 的 HTML／ZIP 解壓放在 **`專案根目錄的 `design-input/`**（與 `.cursor/` 同層）。轉碼時：若仍使用共用 `_handoff`，依其 `globs`；若已改走 `project/` 專案版 handoff，依該檔設定。本倉庫範本見倉庫根的 [design-input/README.md](../design-input/README.md)。

---

## 延伸閱讀

| 檔案 | 內容 |
|------|------|
| [../AGENTS.md](../AGENTS.md) | 跨工具總則範本；`CLAUDE.md` 應指向此檔 |
| [rules/049-agents-md.mdc](rules/049-agents-md.mdc) | `AGENTS.md` 與 `.mdc` 分工、優先序、sync 不涵蓋本檔 |
| [rules/README.md](rules/README.md) | 規則檔列表、編號、Claude Design 三件套、metadata、快速上手 |
| [prd/README.md](prd/README.md) | PRD 結構、`rules/project/`、**衝突裁決與 stub** |
| [scripts/SYNC-CURSOR-RULES.md](../scripts/SYNC-CURSOR-RULES.md) | 同步腳本、**Sync 後檢查清單** |

---

## 複製到新專案時

1. 複製倉庫根 **`AGENTS.md`**，填寫「專案基本資訊」與方括號欄位；刪除未使用的規則索引列。  
2. 建立 **`CLAUDE.md`** 為 `AGENTS.md` 的 symlink（`ln -s AGENTS.md CLAUDE.md`）；無法用 symlink 則改一句指向說明。  
3. 複製 **整個 `.cursor/`**（含本 README、`rules/`、`prd/`）。  
4. 在應用專案根目錄建立 **`design-input/`**（可對照本倉庫範本）。  
5. 依專案需要刪除不需要的規則子集（例如整包移除 `rules/claude-design/`）。**技術棧寫在該專案 `AGENTS.md`／`package.json`／`project/`，不要靠共用規則指定。** `_stack` 僅在 Next 專案被 globs 載入。若 `_handoff` 路徑仍衝突，再 stub 並在 `project/` 建專案版 handoff。  
6. 在 **`prd/`** 依 [prd/README.md](prd/README.md) 自行新增 PRD 檔案（本倉庫不附範本業務內容檔）。

**之後要對齊上游新版**：在本倉庫執行 [scripts/sync-cursor-rules.sh](../scripts/sync-cursor-rules.sh)（說明見 [scripts/SYNC-CURSOR-RULES.md](../scripts/SYNC-CURSOR-RULES.md)），可保留已填 `ci.mdc` 與 `prd/` 內既有 Markdown；**sync 後務必跑檢查清單**（stub 可能被還原）。
