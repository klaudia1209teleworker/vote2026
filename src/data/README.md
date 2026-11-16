# 資料說明

本目錄包含 2026 九合一選舉網站的核心資料檔案。

## 檔案說明

### `candidates.json`
**19,707 位候選人資料**，來自中選會及各縣市選委會官方公告。

- **最近更新**：2026-11-15
- **資料格式**：扁平 JSON 陣列
- **用途**：候選人列表頁及詳細頁面
- **縣市入口**：`/candidates/` 的縣市卡片連到 `/candidates/city/{縣市}/`，依職位列出市長（直接名單）、議員選區、鄉鎮市區、村里長。各職位名單仍在 `/candidates/district/{職位}/{縣市}/…`
- **注意**：村里長（14,115 人）僅顯示列表，不生成個別詳細頁面以控制網站大小

### `electoralDistricts.json`
選舉區劃分對照表，依據中選會 115 年 8 月 20 日公告（A0046）。

- **來源**：[中央選舉委員會公告 中選務字第1153150253號](https://info.cec.gov.tw/vote2026/static/file/2074fdd683844689b5bbdfe0e3ac48b3.pdf)
- **用途**：選票查詢結果連結到正確的選區候選人名單
- **涵蓋範圍**：全部 22 縣市的議員選舉區（含原住民選區）

### `districts.json`
縣市、鄉鎮市區的行政區劃資料，以及六都、省轄市、縣的分類。村里名稱不在此檔，村里長以 `candidates.json` 的 `village` 為準。

- **來源**：中選會 115 年選舉區劃分公告、內政部村里代碼 API
- **用途**：選票查詢的縣市、鄉鎮市區選單與邏輯判斷。村里為選填，選項由村里長候選人的 `village` 在建置時整理，不另存檔。

### `ballotRules.json`
選票領取規則，依據戶籍地類型與原住民身分決定會領到哪些選票。

- **來源**：中選會公告、選罷法
- **用途**：首頁選票查詢結果的生成邏輯

### `bulletin.json`
**選舉公報資料**，包含政見、學歷、經歷等選舉公報刊載內容。

- **最近更新**：2026-11-15
- **涵蓋範圍**：嘉義市（市長 5 人、議員 37 人）
- **資料格式**：以 `縣市|position|選區|姓名|號次` 為 key 的物件
- **用途**：候選人詳細頁面顯示選舉公報內容
- **政見格式**：
  - `platformFormat: "text"`：純文字政見，以 `whitespace-pre-wrap` 保留原始排版
  - `platformFormat: "image"`：圖片政見，對應 `/public/bulletin-pages/` 下的 WebP 圖檔

**新增縣市時**：
1. 從選委會下載選舉公報 PDF
2. 解析候選人資料，依照現有 key 格式加入 `bulletin.json`
3. 若有 `platformFormat: "image"` 的候選人，將 PDF 頁面轉為 WebP 並放入 `/public/bulletin-pages/`
4. 圖檔命名規則：`{PDF UUID 前 8 碼}-p{頁數}.webp`

### `incumbents.json`
**現任議員資料**，包含任職狀態、質詢紀錄等。

- **最近更新**：2026-11-16
- **涵蓋範圍**：621 位比對為現任的議員候選人（跨 21 個議會）
- **資料格式**：以 `縣市|position|選區|姓名|號次` 為 key 的物件
- **用途**：候選人詳細頁面顯示「現任議員」標籤及「現任表現」區塊

**發布規則**：
- 僅顯示 `incumbency.publish: true` 的紀錄
- `needsReview` 紀錄不顯示（異體字、選區編號位移等需人工確認）

**質詢資料類型**（依各議會不同；明細欄位原文照錄）：
- 臺北市：書面質詢（gaz.tcc.gov.tw 公報系統）
- 高雄市：市政總質詢排定時段（cissearch.kcc.gov.tw）
- 臺中市：質詢影音紀錄（vod.tccc.gov.tw；含 `videoUrl`）
- 新竹市：定期會質詢資料 PDF（`documentUrl`／`listedAs`）
- 花蓮縣等：書面質詢 PDF（筆數較少）

候選人頁明細優先顯示：日期、會期、標題／列名、部門、影音／逐字稿／PDF 連結；先 5 則，其餘展開。

**出席率、提案、質詢（候選人詳細頁）**：
- **出席率**：臺北市、臺南市以外，`attendance.status` 為 `missing` 時，tooltip 與註記顯示「議會無法提供相關資料」。
- **臺北市大會（第 14 屆，2026-11-16）**：50 位現任候選人有 `plenary`（0–100）與 `plenaryCounts`。來源是市議會「會議紀錄」類別＝大會的 .doc（129 場；不含談話會與就職典禮）。公式：只出現在出席名單的場次 ÷（出席＋請假＋缺席）；同一場同時列入兩份名單者不計。請假留在分母。委員會未計算，不跨縣市比較，也不套公督盟評鑑權重。重跑：`python3 scripts/taipei_plenary_attendance.py --apply`（需 macOS `textutil`）。
- **臺南市大會（第 4 屆，2026-11-16）**：46 位現任候選人都有 `plenary`。來源是議會會議紀錄 API 的 PDF（359 場中可解析 319 場；下載失敗的場次整場不計）。納入第 N 次會、市政總質詢、部門業務質詢、專案報告；委員會與聯席審查不計。公式與臺北市相同。重跑：`python3 scripts/tainan_plenary_attendance.py --apply`（需 `pypdf`）。
- **質詢／提案數量**：頁面顯示 `該候選人數值／同選區現任者均值`（均值只納入該指標有數值的人，缺失不當 0），並附 tooltip 說明。
- **明細**：優先顯示 5 則，其餘以「展開」顯示（非另外抓取 API）。
- 標題與結果原文照錄；**不做評分、排名或跨縣市正規化比較**。

### `positions.json`
九種職位的詳細說明：職責、待遇、權限、評估標準等。

- **來源**：地方制度法、選罷法、讀字生活 Ep02 影片
- **注意**：待遇數字多以台北市為例，各縣市實際數字不同

---

## 候選人資料結構

### 資料欄位

```json
{
  "county": "臺北市",
  "position": "councilor-municipal",
  "district": "第2選舉區",
  "districtOfficial": "第2選舉區",
  "name": "候選人姓名",
  "number": 1,
  "party": "民主進步黨",
  "partyAsListed": "民主進步黨",
  "status": "公告候選人（選委會11/12公告名單）",
  "sourceUrl": "https://web.cec.gov.tw/api/file/xxx.pdf",
  "sourceArticleUrl": "https://web.cec.gov.tw/tpec/article/12345",
  "sourceDoc": "公告臺北市第15屆市議員選舉候選人名單",
  "asOf": "2026-11-12",
  "registrationSourceUrl": "https://web.cec.gov.tw/api/file/yyy.pdf",
  "registeredOn": "2026-09-02",
  "drawSourceUrl": "https://web.cec.gov.tw/api/file/zzz.pdf",
  "lastVerified": "2026-11-15"
}
```

| 欄位 | 說明 |
|------|------|
| `county` | 縣市名稱 |
| `position` | 職位 ID：`mayor-municipal`、`mayor-county`、`councilor-municipal`、`councilor-county`、`township-mayor`、`township-representative`、`district-mayor`、`district-representative`、`village-chief` |
| `district` | 選區（議員為「第N選舉區」，鄉鎮市長／代表與村里長為鄉鎮市區名） |
| `village` | 村里名。僅村里長有此欄，例如「中寮村」「日祥里」 |
| `districtOfficial` | 選委會公告使用的選區名稱 |
| `name` | 姓名 |
| `number` | 號次（抽籤前為 `null`） |
| `party` | 政黨（無黨籍為 `null`） |
| `partyAsListed` | 選委會公告上的政黨欄位原文（如「無」） |
| `status` | 候選人狀態（見下方說明） |
| `sourceUrl` | 主要資料來源（通常為候選人名單 PDF） |
| `sourceArticleUrl` | 選委會網站公告頁面 |
| `sourceDoc` | 來源文件標題 |
| `asOf` | 資料日期 |
| `registrationSourceUrl` | 登記結果公告連結 |
| `registeredOn` | 登記日期 |
| `drawSourceUrl` | 號次抽籤結果連結 |
| `lastVerified` | 最後驗證日期 |

### 候選人狀態 (`status`)

| 狀態值 | 顯示標籤 | 說明 |
|--------|----------|------|
| `公告候選人（選委會11/12公告名單）` | 已公告 | 選委會已公告正式候選人名單 |
| `已抽籤，號次已公告` | 已抽籤 | 已完成號次抽籤，待公告正式名單 |
| `登記（...）` | 已登記 | 已完成登記，待抽籤或公告 |

### 政黨顯示規則

依據使用者要求：
- 若 `party` 有值：顯示 `party`
- 若 `party` 為 `null` 且 `partyAsListed` 為 `「無」`：顯示「無黨籍推薦」
- 其他情況：顯示 `partyAsListed` 原文

---

## 如何更新資料（11/17 後）

選委會將於 2026 年 11 月 17 日公告完整候選人名單，屆時需更新 `candidates.json`。

### 步驟 1：下載最新公告

1. 前往 [中選會選舉專區](https://info.cec.gov.tw/vote2026/)
2. 或各縣市選委會網站
3. 下載「候選人名單公告」PDF

### 步驟 2：更新 candidates.json

更新方式：
- 將新公告的資料合併到 `candidates.json`
- 更新已有候選人的 `status`、`number`、`sourceUrl`、`asOf` 等欄位
- 確保 `sourceUrl` 指向官方來源

### 步驟 3：驗證資料

```bash
# 檢查 JSON 格式
npm run build

# 驗證候選人數
cat src/data/candidates.json | jq 'length'

# 檢查特定縣市
cat src/data/candidates.json | jq '[.[] | select(.county == "臺北市")] | length'
```

### 步驟 4：測試建置

```bash
npm run build
npm run preview
```

檢查：
- 候選人列表頁顯示正確
- 詳細頁連結可正常訪問
- 狀態徽章顯示正確

---

## 資料來源

### 候選人名單
- [中選會 115 選舉專區](https://info.cec.gov.tw/vote2026/)
- [選舉公報](https://bulletin.cec.gov.tw/)
- 各縣市選委會網站（https://web.cec.gov.tw/）

### 選舉區劃分
- [中選會公告 A0046](https://info.cec.gov.tw/vote2026/static/file/2074fdd683844689b5bbdfe0e3ac48b3.pdf)

### 各縣市選委會

| 縣市 | 網址 |
|------|------|
| 臺北市 | https://web.cec.gov.tw/tpec/ |
| 新北市 | https://web.cec.gov.tw/tpcec/ |
| 桃園市 | https://web.cec.gov.tw/tyec/ |
| 臺中市 | https://web.cec.gov.tw/txec/ |
| 臺南市 | https://web.cec.gov.tw/tnec/ |
| 高雄市 | https://web.cec.gov.tw/ksec/ |
| 基隆市 | https://web.cec.gov.tw/klec/ |
| 新竹市 | https://web.cec.gov.tw/hcec/ |
| 嘉義市 | https://web.cec.gov.tw/cyec/ |
| 新竹縣 | https://web.cec.gov.tw/hchec/ |
| 苗栗縣 | https://web.cec.gov.tw/mlec/ |
| 彰化縣 | https://web.cec.gov.tw/chec/ |
| 南投縣 | https://web.cec.gov.tw/ntec/ |
| 雲林縣 | https://web.cec.gov.tw/ylec/ |
| 嘉義縣 | https://web.cec.gov.tw/cyhec/ |
| 屏東縣 | https://web.cec.gov.tw/ptec/ |
| 宜蘭縣 | https://web.cec.gov.tw/ilec/ |
| 花蓮縣 | https://web.cec.gov.tw/hlec/ |
| 臺東縣 | https://web.cec.gov.tw/ttec/ |
| 澎湖縣 | https://web.cec.gov.tw/phec/ |
| 金門縣 | https://web.cec.gov.tw/kmec/ |
| 連江縣 | https://web.cec.gov.tw/mtsec/ |

---

## 貢獻指南

### 原則

1. **僅使用官方來源**
   - 選委會公告 PDF
   - 選舉公報
   - 不可使用媒體報導或民間整理

2. **保持中立**
   - 不可包含主觀評價
   - 不可包含推薦或排名
   - 僅陳述可驗證的事實

3. **完整來源**
   - 每筆資料必須包含 `sourceUrl`
   - 標明 `asOf` 與 `lastVerified`

### 提交流程

1. Fork 本專案
2. 修改 `candidates.json`
3. 執行 `npm run build` 確認建置成功
4. 在 PR 說明中列出所有資料來源
5. 等待 review

---

## 建置限制

為符合 GitHub Pages 限制（1 GB 網站大小、~10 分鐘建置時間）：

- **村里長候選人**（14,115 人）不生成個別詳細頁面
- 列表頁以鄉鎮市區為一頁，依 `village` 分組，並可用「篩選村里」或網址 `?village=` 只顯示一里
- 首頁選票查詢在鄉鎮市區之後可選村里；有選時，里長的「候選人」連結帶 `?village=`
- 其他職位候選人（5,592 人）生成詳細頁面
