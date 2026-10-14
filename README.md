# XIAI Jewelry Website · 玺爱官网

玺爱珠宝品牌官网（静态多页面网站）。正式地址 https://sophia-zhang101.github.io （GitHub Pages，国内可访问）；Vercel 上的 xiai-website.vercel.app 为备用，国内访问不稳定。

## 页面
- `/` 首页 · `/products` 全部产品 · `/products/<品类>` 品类页（necklaces / earrings / rings / bracelets / pendants / brooches）
- `/products/<货号>` 产品详情页（32 款）
- `/pearl-guide` 珍珠指南 · `/our-story` 品牌故事 · `/wholesale` 批发与定制 · `/contact` 联系与常见问题

## 怎么改
- 产品资料：`data/products.json`（名称、参数、文案、FAQ、图片），全部来自企业 SKU 信息收集表，不要加表里没有的款式。
- 页面结构和文案：`scripts/build_site.py`；样式：`assets/site.css`；交互：`assets/site.js`。
- 改完运行 `python3 scripts/build_site.py`，会重新生成所有 HTML 和 `sitemap.xml`（不要手改生成出来的 HTML）。
- 产品图：`images/products/<货号>/`（白底原图，最长边 1400px，已去掉带水印/海报字的图）。
- 模特图：`images/campaign/`，是用 Canva AI 以真品图为参考生成的，页面上都标注了「AI-generated」；`build_site.py` 里的 `CAMPAIGN` 决定哪张图用在哪里，每张图必须对应一款真实货号。

## 部署
- GitHub Pages：把整个目录同步到 `Sophia-ZHANG101.github.io` 仓库的 main 分支。
- Vercel：推送本仓库 main 分支即可自动部署。
