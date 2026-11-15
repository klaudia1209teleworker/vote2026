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
候選人資料。每位候選人有獨立的詳細頁面，網址格式為 `/vote2026/candidates/[id]/`。

- **狀態**：正式名單待 11/17 公告後更新
- **重要**：不可包含 `isSample: true` 的測試資料

---

## 候選人資料結構 v2

### 基本資料（必填）

```json
{
  "id": "councilor-taipei-daan-1",
  "name": "候選人姓名",
  "number": 1,
  "party": "政黨名稱",
  "position": "councilor-municipal",
  "city": "臺北市",
  "district": "第四選區（大安區）",
  "isIncumbent": true,
  "officialSourceUrl": "https://info.cec.gov.tw/vote2026/...",
  "lastVerified": "2026-11-17"
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `id` | ✅ | 唯一識別碼，用於 URL。建議格式：`{position}-{city}-{district}-{number}` |
| `name` | ✅ | 姓名 |
| `number` | ✅ | 號次 |
| `party` | | 政黨，無黨籍填 `null` |
| `position` | ✅ | 職位 ID，對應 `positions.json` |
| `city` | ✅ | 縣市 |
| `district` | ✅ | 選區 |
| `isIncumbent` | | 是否為現任 |
| `officialSourceUrl` | ✅ | 官方來源連結 |
| `lastVerified` | ✅ | 最後驗證日期 `YYYY-MM-DD` |

---

### 政見 `platform`

來源：選舉公報 (bulletin.cec.gov.tw)

```json
{
  "platform": {
    "content": "政見原文...",
    "bulletinUrl": "https://bulletin.cec.gov.tw/01選舉公報/...",
    "bulletinPage": 5,
    "asOf": "2026-11-20"
  }
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `content` | | 政見原文（選舉公報內容） |
| `bulletinUrl` | ✅ | 選舉公報 PDF 連結 |
| `bulletinPage` | | 公報頁碼 |
| `asOf` | | 公報發布日期 |

**來源查找**：
1. 前往 https://bulletin.cec.gov.tw/
2. 選擇「01選舉公報」→ 對應職務 → 115年
3. 下載該選區的 PDF，找到候選人頁面
4. 複製政見原文，記錄頁碼

---

### 過去的施政/問政紀錄 `pastRecords`

適用於：現任或曾任公職者

```json
{
  "pastRecords": [
    {
      "title": "質詢交通局長關於行人安全改善進度",
      "date": "2025-05-15",
      "category": "質詢",
      "description": "要求交通局說明危險路口改善時程...",
      "sourceUrl": "https://gaz.tcc.gov.tw/...",
      "sourceName": "臺北市議會電子公報"
    }
  ]
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `title` | ✅ | 紀錄標題/摘要 |
| `date` | ✅ | 日期 `YYYY-MM-DD` 或 `YYYY-MM` |
| `category` | | 類別：質詢、提案、會勘、其他 |
| `description` | | 詳細說明 |
| `sourceUrl` | ✅ | 官方來源連結 |
| `sourceName` | | 來源名稱 |

**來源查找**：
- 臺北市：https://gaz.tcc.gov.tw/ （電子公報）
- 高雄市：https://cissearch.kcc.gov.tw/
- 其他：https://journal.th.gov.tw/ （議事錄總庫）

---

### 出席紀錄 `attendance`

大會與委員會出席分開記錄。

```json
{
  "attendance": {
    "general": {
      "attended": 95,
      "total": 100,
      "rate": "95%",
      "term": "第 14 屆",
      "sessionPeriod": "2022-12-25 至 2026-10-31",
      "sourceUrl": "https://www.tcc.gov.tw/...",
      "sourceName": "臺北市議會",
      "asOf": "2026-10-31"
    },
    "committee": {
      "attended": 48,
      "total": 50,
      "rate": "96%",
      "committeeName": "交通委員會",
      "term": "第 14 屆",
      "sessionPeriod": "2022-12-25 至 2026-10-31",
      "sourceUrl": "https://www.tcc.gov.tw/...",
      "sourceName": "臺北市議會",
      "asOf": "2026-10-31"
    }
  }
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `attended` | | 出席次數 |
| `total` | | 應出席次數 |
| `rate` | | 出席率（百分比字串） |
| `term` | ✅ | 屆期 |
| `sessionPeriod` | ✅ | 會期期間 |
| `committeeName` | | 委員會名稱（僅委員會） |
| `sourceUrl` | ✅ | 官方來源連結 |
| `sourceName` | | 來源名稱 |
| `asOf` | | 資料截至日期 |

**來源查找**：
- 各縣市議會官網的「議事資訊」或「出席統計」
- 部分議會有公開的出席率報表

---

### 提案紀錄 `proposals`

```json
{
  "proposals": [
    {
      "title": "建請市府增設行人專用號誌",
      "date": "2025-03-10",
      "status": "通過",
      "term": "第 14 屆第 5 次定期大會",
      "sourceUrl": "https://www.tcc.gov.tw/...",
      "sourceName": "臺北市議會議事錄"
    },
    {
      "title": "建請市府檢討停車收費標準",
      "date": "2025-06-20",
      "status": "待審",
      "term": "第 14 屆第 6 次定期大會",
      "sourceUrl": "https://www.tcc.gov.tw/...",
      "sourceName": "臺北市議會議事錄"
    }
  ]
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `title` | ✅ | 提案標題 |
| `date` | ✅ | 提案日期 `YYYY-MM-DD` |
| `status` | ✅ | 狀態：`通過`、`待審`、`撤回`、`否決`、`其他` |
| `term` | | 屆期/會期 |
| `sourceUrl` | ✅ | 官方來源連結 |
| `sourceName` | | 來源名稱 |

**成功提案率計算**：
- 系統自動計算：`通過數 / 總提案數`
- **不可自行填入成功提案率**
- 顯示時會同時顯示分子、分母、統計期間

---

### 新人候選人資料 `newcomerProfile`

適用於：無公職經歷者

```json
{
  "newcomerProfile": {
    "education": [
      {
        "degree": "碩士",
        "school": "國立臺灣大學",
        "field": "都市計劃研究所",
        "year": "2018",
        "sourceUrl": "https://bulletin.cec.gov.tw/..."
      }
    ],
    "experience": [
      {
        "title": "都市規劃師",
        "organization": "OO建築師事務所",
        "period": "2018-2026",
        "sourceUrl": "https://bulletin.cec.gov.tw/..."
      }
    ],
    "publicParticipation": [
      {
        "activity": "社區改造志工",
        "role": "規劃顧問",
        "date": "2022-2024",
        "sourceUrl": "https://...",
        "sourceName": "XX社區發展協會"
      }
    ]
  }
}
```

**學歷 `education`**：

| 欄位 | 說明 |
|------|------|
| `degree` | 學位 |
| `school` | 學校 |
| `field` | 科系 |
| `year` | 畢業年份 |
| `sourceUrl` | 來源（通常為選舉公報） |

**經歷 `experience`**：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `title` | ✅ | 職稱 |
| `organization` | | 機構/公司 |
| `period` | | 期間 |
| `sourceUrl` | | 來源連結 |

**公共參與 `publicParticipation`**：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `activity` | ✅ | 活動名稱 |
| `role` | | 角色 |
| `date` | | 日期/期間 |
| `sourceUrl` | | 來源連結 |
| `sourceName` | | 來源名稱 |

---

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
- 選區列表頁：`/vote2026/candidates/district/councilor-municipal/臺北市/第五選區/`
- 候選人詳細頁：`/vote2026/candidates/[candidate-id]/`

### 資料來源原則

1. **僅使用官方來源**
   - 選舉公報 (bulletin.cec.gov.tw)
   - 議會紀錄（各縣市議會官網）
   - 議事錄總庫 (journal.th.gov.tw)
   - 政府公報、公告

2. **禁止使用**
   - 媒體報導作為唯一來源
   - 社群媒體貼文
   - 未經驗證的民間整理
   - 候選人自述（除非來自選舉公報）

### 資料驗證要求

- 每筆資料必須包含 `sourceUrl`
- 出席率、提案紀錄需標明 `term`（屆期）和 `sessionPeriod`（會期期間）
- 時間敏感資料需標明 `asOf`（資料截至日期）
- 無法驗證的欄位留空，不可捏造

### 成功提案率規則

- **不可自行填入成功提案率**
- 系統根據 `proposals` 欄位自動計算
- 計算公式：`status === '通過'` 的數量 / 總提案數
- 頁面會顯示：百分比、分子、分母、統計期間

### 中立性原則

- 不可包含主觀評價（「優秀」「差勁」）
- 不可包含推薦或排名
- 不可使用顏色暗示好壞
- 僅陳述可驗證的事實
- 候選人依號次排列（號次未公告前依姓名排列）

### 提交流程

1. Fork 本專案
2. 修改 `candidates.json`
3. 執行 `npm run build` 確認建置成功
4. 在 PR 說明中列出所有資料來源
5. 等待 review

---

## 官方資料連結

### 選舉公報與候選人
- [中選會 115 選舉專區](https://info.cec.gov.tw/vote2026/)
- [選舉公報](https://bulletin.cec.gov.tw/)

### 議會紀錄
- [地方議會議事錄總庫](https://journal.th.gov.tw/)
- [臺北市議會電子公報](https://gaz.tcc.gov.tw/)
- [高雄市議會議事資訊系統](https://cissearch.kcc.gov.tw/)

### 各縣市議會
- 臺北市：https://www.tcc.gov.tw/
- 新北市：https://www.ntp.gov.tw/
- 桃園市：https://www.tycc.gov.tw/
- 臺中市：https://www.tccc.gov.tw/
- 臺南市：https://www.tncc.gov.tw/
- 高雄市：https://www.kcc.gov.tw/

更多議會連結見：https://journal.th.gov.tw/link.php
