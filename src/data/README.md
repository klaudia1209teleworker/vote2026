# 資料說明

本目錄包含 2026 九合一選舉網站的核心資料檔案。

## 檔案說明

### `districts.json`
縣市、鄉鎮市區、村里的行政區劃資料，以及六都、省轄市、縣的分類。

- **來源**：中選會 115 年選舉區劃分公告、內政部村里代碼 API
- **用途**：選票查詢功能的選單與邏輯判斷

### `ballotRules.json`
選票領取規則，依據戶籍地類型與原住民身分決定會領到哪些選票。

- **來源**：中選會公告、選罷法
- **用途**：首頁選票查詢結果的生成邏輯

### `positions.json`
九種職位的詳細說明：職責、待遇、權限、評估標準等。

- **來源**：地方制度法、選罷法、讀字生活 Ep02 影片
- **注意**：待遇數字多以台北市為例，各縣市實際數字不同

### `candidates.json`
候選人資料架構與範例資料。

- **狀態**：正式名單待 11/17 公告後更新
- **架構**：見下方「候選人資料結構」

## 候選人資料結構

```json
{
  "id": "唯一識別碼（建議格式：position-city-district-number）",
  "name": "姓名",
  "number": 1,
  "party": "政黨名稱（無黨籍填 null）",
  "position": "職位 ID（對應 positions.json）",
  "city": "縣市",
  "district": "選區",
  "bulletinUrl": "選舉公報連結",
  "officialSourceUrl": "官方來源連結（必填）",
  "lastVerified": "最後驗證日期 YYYY-MM-DD（必填）",
  "isIncumbent": true,
  "checks": {
    "incumbent": {
      "councilAttendance": {
        "general": "大會出席率",
        "committee": "委員會出席率",
        "source": "來源連結"
      },
      "interpellations": [
        {
          "topic": "質詢主題",
          "date": "日期",
          "followUp": true,
          "source": "來源連結"
        }
      ]
    },
    "newcomer": {
      "professionalBackground": "專業背景",
      "publicParticipation": [
        {
          "activity": "活動名稱",
          "role": "角色",
          "source": "來源連結"
        }
      ]
    }
  }
}
```

## 貢獻指南

### 資料來源原則

1. **僅使用官方來源**
   - 中選會公告與選舉公報
   - 議會紀錄（議事錄、電子公報）
   - 政府開放資料平台
   - 法規資料庫

2. **禁止使用**
   - 媒體報導作為唯一來源
   - 社群媒體貼文（除非為驗證專業背景）
   - 未經驗證的民間整理

### 資料驗證要求

- 每筆資料必須包含 `officialSourceUrl`（官方來源連結）
- 每筆資料必須包含 `lastVerified`（驗證日期）
- 無法驗證的欄位留空，不可捏造

### 中立性原則

- 不可包含主觀評價（「優秀」「差勁」）
- 不可包含推薦或排名
- 僅陳述可驗證的事實

### 提交流程

1. Fork 本專案
2. 修改 `candidates.json`
3. 在 PR 說明中列出所有資料來源
4. 等待 review

## 官方資料連結

- [中選會 115 選舉專區](https://info.cec.gov.tw/vote2026/)
- [選舉公報](https://bulletin.cec.gov.tw/)
- [地方議會議事錄總庫](https://journal.th.gov.tw/)
- [臺北市議會電子公報](https://gaz.tcc.gov.tw/)
- [高雄市議會議事資訊系統](https://cissearch.kcc.gov.tw/)
