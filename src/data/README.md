# 資料說明

本目錄包含 2026 九合一選舉網站的核心資料檔案。

## 檔案說明

### `districts.json`
縣市、鄉鎮市區、村里的行政區劃資料，以及六都、省轄市、縣的分類。

- **來源**：中選會 115 年選舉區劃分公告、內政部村里代碼 API
- **用途**：選票查詢功能的選單與邏輯判斷

### `electoralDistricts.json`
選舉區劃分對照表，將行政區對應到選舉區（尤其是議員選區）。

- **來源**：中選會 115 年選舉區劃分公告
- **用途**：選票查詢結果連結到正確的選區候選人名單
- **注意**：部分選區依里劃分，詳見中選會公告

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

### 新增候選人資料

#### 步驟 1：確認選區

每位候選人必須填入正確的 `position`、`city`、`district` 欄位：

| 職位 | position ID | district 格式 | 範例 |
|------|-------------|--------------|------|
| 直轄市長 | `mayor-municipal` | （留空或填縣市名） | `臺北市` |
| 縣市長 | `mayor-county` | （留空或填縣市名） | `宜蘭縣` |
| 直轄市議員 | `councilor-municipal` | 第X選區（依中選會公告） | `第五選區` |
| 縣市議員 | `councilor-county` | 第X選區 | `第一選區` |
| 鄉鎮市長 | `township-mayor` | 鄉鎮市區名 | `宜蘭市` |
| 鄉鎮市民代表 | `township-representative` | 鄉鎮市區名 | `羅東鎮` |
| 山地原住民區區長 | `district-mayor` | 區名 | `烏來區` |
| 區民代表 | `district-representative` | 區名 | `復興區` |
| 村里長 | `village-chief` | 鄉鎮市區名或完整村里名 | `萬華區` 或 `青年里` |

#### 步驟 2：查詢選區對照

台北市、新北市議員選區對照表已建置於 `electoralDistricts.json`，可查詢行政區對應的選舉區：

```javascript
// 例：萬華區 → 第五選區
electoralDistricts.adminToElectoralMapping["councilor-municipal"]["臺北市"]["萬華區"]
// { "districtId": "taipei-5", "districtName": "第五選區" }
```

其他縣市的選區對照待補充，可參考中選會公告自行比對。

#### 步驟 3：填寫候選人資料

在 `candidates.json` 的 `candidates` 陣列新增一筆資料：

```json
{
  "id": "councilor-municipal-taipei-5-1",
  "name": "候選人姓名",
  "number": 1,
  "party": "政黨名稱",
  "position": "councilor-municipal",
  "city": "臺北市",
  "district": "第五選區",
  "bulletinUrl": "https://bulletin.cec.gov.tw/...",
  "officialSourceUrl": "https://info.cec.gov.tw/vote2026/...",
  "lastVerified": "2026-11-17",
  "isIncumbent": false,
  "isSample": false
}
```

**重要：**
- `isSample` 必須設為 `false`，否則資料不會顯示在公開頁面
- `officialSourceUrl` 和 `lastVerified` 為必填欄位

#### 步驟 4：驗證頁面生成

新增資料後，執行 `npm run build`，確認候選人出現在對應的選區頁面：
- 例：臺北市第五選區議員 → `/vote2026/candidates/district/councilor-municipal/臺北市/第五選區/`

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
- 候選人依號次排列（號次未公告前依姓名排列）

### 提交流程

1. Fork 本專案
2. 修改 `candidates.json`
3. 執行 `npm run build` 確認建置成功
4. 在 PR 說明中列出所有資料來源
5. 等待 review

## 官方資料連結

- [中選會 115 選舉專區](https://info.cec.gov.tw/vote2026/)
- [選舉公報](https://bulletin.cec.gov.tw/)
- [地方議會議事錄總庫](https://journal.th.gov.tw/)
- [臺北市議會電子公報](https://gaz.tcc.gov.tw/)
- [高雄市議會議事資訊系統](https://cissearch.kcc.gov.tw/)
