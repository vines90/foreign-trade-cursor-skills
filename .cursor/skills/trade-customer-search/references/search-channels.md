# 4 个搜索通道详解

> 本 skill 默认启用 3 个通道（Maps + Google + Facebook），第 4 个（Contact Enrichment）默认关闭。
> LinkedIn 通道**不在本 skill 内**，由下游 `b2b-customer-research` 单点深背调时按需调用。

---

## 通道 1：Google Maps（实体店 / 本地经销商）

### 适用客户类型
- ✅ retailer / wholesaler / dealer（有实体店面）
- ❌ 纯线上品牌、平台卖家

### Apify Actor
- **主用**：`compass/crawler-google-places`
- **备用**：`compass/google-maps-extractor`

### 输入参数模板

```json
{
  "searchStringsArray": [
    "{search_term} in {city}, {country}"
  ],
  "locationQuery": "{city}, {country}",
  "maxCrawledPlacesPerSearch": 30,
  "language": "en",
  "scrapePlaceDetailPage": true,
  "scrapeContacts": true,
  "scrapeReviewsPersonalData": false,
  "skipClosedPlaces": true
}
```

**关键参数说明**：
- `searchStringsArray`：每条 1 个查询，多查询用数组并行
- `language`：搜索语言，按国家自动推断（参见 i18n-keywords.md）
- `scrapeContacts: true`：拉电话/邮箱/官网（核心）
- `skipClosedPlaces: true`：自动跳过已关停商家

### 输出关键字段

| Apify 输出字段 | 映射到统一 schema |
|---|---|
| `title` | company_name |
| `website` | website |
| `phone` | phone |
| `address` | address |
| `city` | city |
| `countryCode` | country |
| `totalScore` | google_rating |
| `reviewsCount` | reviews_count |
| `categories` | （用于客户类型推断）|
| `imageUrl` | （忽略）|

### 默认成本
- 30 商家 × $0.0035 = **~$0.10/城市**
- 5 城市并发 = **~$0.50/任务**

---

## 通道 2：Google 搜索（纯线上 / 品牌方）

### 适用客户类型
- ✅ importer / distributor / brand / wholesaler（线上为主）
- ✅ 海关数据/招商页/RFQ 触达
- ❌ 实体零售（信息少）

### Apify Actor
- **主用**：`apify/google-search-scraper`

### 输入参数模板

```json
{
  "queries": [
    "{advanced_query_1}",
    "{advanced_query_2}"
  ],
  "resultsPerPage": 30,
  "maxPagesPerQuery": 1,
  "languageCode": "en",
  "countryCode": "DE",
  "mobileResults": false,
  "saveHtml": false,
  "includeUnfilteredResults": false
}
```

### 高级查询模板（5 类）

按客户类型选择不同模板：

#### 模板 A：找经销商招募信息
```
"{product_local}" "{distributor_local}" site:.{country_tld} -inurl:alibaba -inurl:amazon
"{distributor wanted}" "{product_local}" "{country_local}"
"become a {dealer_local}" "{product_local}" filetype:pdf
```

#### 模板 B：找进口商
```
"{importer_local}" "{product_local}" "{country_local}" -inurl:alibaba
"{product_local}" "import" intext:"{contact_us_local}" site:.{country_tld}
```

#### 模板 C：找批发商
```
"{wholesale_local}" "{product_local}" site:.{country_tld}
"{product_local}" "{B2B_local}" minimum order intext:"{rfq_local}"
```

#### 模板 D：找零售连锁
```
"{retailer_local}" "{product_local}" "{country_local}" -inurl:alibaba
"buy {product_local}" intext:"{store locator}" site:.{country_tld}
```

#### 模板 E：找品牌方
```
"{product_local} brand" "{country_local}" intext:"{about us_local}"
"{product_local}" intext:"founded" intext:"{country_local}" -inurl:wikipedia
```

### 输出关键字段

| Apify 输出字段 | 映射 |
|---|---|
| `organicResults[].title` | company_name（需清洗）|
| `organicResults[].url` | website（取 root domain）|
| `organicResults[].description` | （用于推断客户类型）|

### 后处理（必做）

1. URL 标准化为 root domain（去掉 path）
2. 去重（同一 domain 只保留 1 条）
3. 黑名单过滤（参见 domain-blacklist.txt）
4. 国家校验（域名 TLD vs 目标国 / `description` 提及国家）

### 默认成本
- 5 query × 30 结果 × $0.0008 = **~$0.12/任务**

---

## 通道 3：Facebook Pages（中小品牌 / 社媒活跃零售）

### 适用客户类型
- ✅ retailer / brand（有 FB 主页）
- ✅ 直接拿邮箱/电话/地址（FB 联系信息往往比官网完整）
- ❌ 大型 B2B 进口商（FB 不活跃）

### Apify Actor
- **主用**：`apify/facebook-pages-scraper`（基础信息）
- **备用**：`apify/facebook-page-contact-information`（专门拉联系信息）
- **搜索用**：`apify/facebook-search-scraper`（按关键词搜索 Page）

### 输入参数模板（搜索 + 拉详情）

#### Step A: 搜索 Pages
```json
{
  "queries": ["{product_local} {city}"],
  "searchType": "pages",
  "maxResultsPerQuery": 30,
  "country": "DE"
}
```

#### Step B: 对前 N 个 Page 拉联系信息
```json
{
  "startUrls": [
    {"url": "https://facebook.com/page1"}
  ]
}
```

### 输出关键字段

| Facebook 字段 | 映射 |
|---|---|
| `title` / `name` | company_name |
| `website` | website |
| `email` | emails[] |
| `phone` | phone |
| `address` | address |
| `categories` | （客户类型推断）|
| `likes` | （活跃度信号）|

### 默认成本
- 30 search + 15 详情 = **~$0.20/任务**

---

## 通道 4：Contact Info Enrichment（默认关闭）

### 何时启用
- 用户在输入显式设置 `enable_enrichment: true`
- 或下游 skill（如 `b2b-customer-research`）需要邮箱时单独调用

### Apify Actor
- **主用**：`vdrmota/contact-info-scraper`
- **备用**：`poidata/google-maps-email-extractor`

### 输入参数模板

```json
{
  "startUrls": [
    {"url": "https://acme.de"},
    {"url": "https://other.de"}
  ],
  "maxDepth": 2,
  "maxRequestsPerStartUrl": 8,
  "considerChildFrames": false
}
```

### 输出字段

| 字段 | 说明 |
|---|---|
| `emails[]` | 邮箱列表（含 mailto/页脚/联系页）|
| `phones[]` | 电话列表 |
| `linkedIns[]` | LinkedIn 链接 |
| `twitters[]` | Twitter |
| `instagrams[]` | Instagram |
| `facebooks[]` | Facebook |

### 默认成本
- 50 URL × $0.008 = **~$0.40/任务**

### 默认关闭原因
- 本 skill 定位"找客户名单"，不涉及深度联系人
- 富化由下游单家深背调时调用，避免对低质量客户浪费 credits

---

## 通道选择决策表

| 客户类型 | 主通道 | 次通道 | 富化默认 |
|---|---|---|---|
| retailer | Maps | FB Pages | 关 |
| wholesaler | Google + Maps | FB Pages | 关 |
| importer | Google | - | 关 |
| distributor | Google | - | 关 |
| dealer | Maps + Google | - | 关 |
| brand | Google | FB Pages | 关 |
| supplier | Google | - | 关 |
| 未指定 | Google + Maps | - | 关 |

---

## 多通道结果合并规则

### 去重键（按优先级）
1. 标准化后的 root domain（`acme.de` == `https://www.acme.de/`）
2. 公司名（精确匹配，去除 GmbH / Inc / Ltd 等公司类型后缀后再比）
3. 电话号码（标准化为 E.164 格式）

### 字段合并（同一公司多通道命中时）
- `emails`：多通道并集
- `phone`：选择最完整的（含国际区号优先）
- `address`：Maps 优先（更准）
- `social`：FB 通道优先
- `google_rating`：仅 Maps 有
- `source`：拼接所有通道，如 `[google-maps, google-search]`
- `confidence`：见下表

### Confidence 评分规则

| 命中通道数 | 有官网 | 国家匹配 | confidence |
|---|---|---|---|
| ≥2 | ✅ | ✅ | high |
| 1 | ✅ | ✅ | medium |
| 1 | ❌ | ✅ | low |
| 任意 | 任意 | ❌ | low |

---

## 反垃圾过滤（所有通道通用）

### 强制剔除（confidence 直接 = skip）
- 域名在 domain-blacklist.txt
- URL 含 `/seller/` `/store/` 但 root domain 是平台（amazon/ebay/alibaba）
- 公司名含明显同行特征（如 "Manufacturer" + 来源中国）
- TLD = .gov / .edu / .org（一般非贸易商）

### 弱过滤（confidence 降级到 low）
- 公司名是分类目录页（"Top 10..."、"Best..."）
- description 含 "directory" / "list of"
- 同 domain 有 >5 条命中（聚合站特征）
