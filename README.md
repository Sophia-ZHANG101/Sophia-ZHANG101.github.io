# XIAI Jewelry Website · 玺爱官网

玺爱珠宝品牌官网（静态页面）。正式地址 https://sophia-zhang101.github.io （GitHub Pages，国内可访问）；Vercel 上的 xiai-website.vercel.app 为备用，国内访问不稳定。

- `index.html` — 首页
- `images/` — 产品图
- `products/index.html` — 全部产品总览页 `/products`，按品类分组（由脚本生成）
- `products/<货号>.html` — 产品详情页（由脚本生成，不要手改），线上地址 `/products/<货号>`
- `data/products.json` — 产品详情页的数据：名称、参数、文案、FAQ、图片
- `scripts/build_products.py` — 改完 `data/products.json` 或首页样式后运行 `python3 scripts/build_products.py` 重新生成详情页、总览页和 sitemap.xml
- `images/products/<货号>/` — 详情页图库（白底原图，1400px）
- `vercel.json` — Vercel 配置
