# Daily Brief

数据驱动的每日看板。只需更新 `data/YYYY-MM-DD.json` 与 `data/index.json`。

## 添加新的一天
1. 复制模板：`data/2026-01-30.json` → `data/YYYY-MM-DD.json`
2. 更新 `data/index.json` 头部新增一条日期
3. 复制页面模板：`daily/2026-01-30.html` → `daily/YYYY-MM-DD.html` 并改 date
4. 提交并推送，Vercel 自动发布
