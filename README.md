# 2026 九合一選舉資訊網站

台灣 2026 年地方公職人員選舉（九合一選舉）資訊網站。

- **投票日**：2026 年 11 月 28 日（星期六）08:00 - 16:00
- **同日公投**：全國性公民投票案第 22 案（18 歲以上可投）
- **部署位置**：GitHub Pages (`/vote2026/`)

## 功能

1. **首頁：我會拿到哪幾張票**  
   選擇縣市 → 鄉鎮市區 → 原住民身分，查詢您會領取的選票清單

2. **九種職務介紹**  
   市長、議員、里長等九種職位的職責、待遇、評估標準

3. **怎麼判斷候選人**  
   設定底線、查詢出席率與質詢紀錄、觀察里長的方法

4. **投票當天須知**  
   時間、證件、圈選工具、禁止事項、公投說明

5. **市長、議員、里長怎麼合作**  
   萬華路燈案例說明三種角色的協作

6. **候選人資訊**  
   資料架構已建立，正式名單待 11/17 公告後更新

7. **關於/資料來源**  
   免責聲明、資料來源列表、驗證狀態

## 技術

- [Astro](https://astro.build/) - 靜態網站框架
- [Tailwind CSS](https://tailwindcss.com/) v4 - 樣式
- GitHub Actions - 自動部署至 GitHub Pages

## 開發

```bash
# 安裝依賴
npm install

# 開發伺服器
npm run dev

# 建置
npm run build

# 預覽建置結果
npm run preview
```

## 部署

推送至 `main` 分支時，GitHub Actions 會自動建置並部署至 GitHub Pages。

### 啟用 GitHub Pages

1. 前往 Repository Settings → Pages
2. Source 選擇「GitHub Actions」
3. 推送任何變更觸發部署

## 資料來源

- [中選會 115 選舉專區](https://info.cec.gov.tw/vote2026/)
- [選舉公報](https://bulletin.cec.gov.tw/)
- [地方議會議事錄總庫](https://journal.th.gov.tw/)
- [地方制度法](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0040003)

詳見 `/about` 頁面的完整資料來源列表。

## 重要聲明

**本站非中央選舉委員會官方網站。所有資訊以[中選會官方公告](https://www.cec.gov.tw/)為準。**

本站不提供候選人推薦、排名或民調資訊。

## 授權

程式碼以 MIT License 授權。

---

製作：Kay Chen  
最後更新：2026-11-15
