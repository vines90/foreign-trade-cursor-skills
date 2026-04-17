---
name: trade-customer-search
description: 外贸潜客搜索：用户只给出产品和目标市场，自动通过 Google Maps + Google 搜索 + Facebook Pages 三通道搜索潜在客户，输出标准化潜客名单（含官网/电话/地址/Facebook，不含深度联系人）。自动多语言查询、多城市覆盖、域名黑名单过滤、跨通道去重。当用户提到"找客户"、"找海外潜客"、"搜潜在客户"、"开发新客户"、"在XX找经销商/进口商/批发商/零售商"、"挖客户名单"时使用。不做深度背调（→ b2b-customer-research），不写飞书表（→ bitable-trade-customer），不评分发邮件（→ auto-trade-customer-development）。
---

# 外贸潜客搜索

通过多通道并行搜索 + 跨通道去重 + 反垃圾过滤，从 0 到 1 帮用户挖出目标市场的潜客名单。

## 适用范围

| 场景 | 是否适用 |
|---|---|
| 已有官网，要做深度背调 | ❌ 用 `b2b-customer-research` |
| 把背调结果存档 | ❌ 用 `bitable-trade-customer` |
| 全自动找+背调+发信 | ❌ 用 `auto-trade-customer-development`（它会调用本 skill）|
| 仅需"找一份名单"，自己人工筛选 | ✅ |
| 给 `auto-trade-customer-development` 提供输入 | ✅ |
| 探索新市场可行性 | ✅ |

## 依赖

- `apify-ultimate-scraper` skill（脚本 + Apify token）
- 项目根 `.env` 含 `APIFY_TOKEN`

## 输入契约

最少需要 2 个字段：

```yaml
product: "硅胶宠物碗"             # 必填，产品类目（中文/英文均可，会自动翻译）
target_market: "Germany"         # 必填，国家/城市/大区均可
                                  # 例: "DE", "Berlin, Germany", "Western Europe"

# === 可选 ===
customer_types:                   # 默认 [distributor, importer, wholesaler]
  - retailer
  - wholesaler
  - distributor
  - importer
  - dealer
  - brand
city_list: null                   # 留空则按 city-lists.md 自动展开
max_cities: 5                     # 默认 5 个城市，深度模式可设 10
max_results_per_city: 30          # 默认 30
language_override: null           # 默认按国家自动推断
enable_enrichment: false          # 默认关，仅产出官网；下游再富化
extra_blacklist_domains: []       # 项目自定义黑名单
budget_credits_usd: 1.0           # Apify 成本上限
output_dir: "output/leads"        # 输出目录
```

## 工作流

```
Task Progress:
- [ ] Step 0: 解析输入 + 检查 APIFY_TOKEN
- [ ] Step 1: 展开城市清单 + 推断语言
- [ ] Step 2: 翻译产品/客户类型为本地词
- [ ] Step 3: 构造各通道查询计划 + 预算估算
- [ ] Step 4: 并行执行 3 通道
- [ ] Step 5: 跨通道合并 + 去重 + 黑名单过滤 + Confidence 评分
- [ ] Step 6: (可选) 调用 Step 7 做 enrichment
- [ ] Step 7: 输出 CSV + JSON + 摘要报告
```

### Step 0: 输入校验

```bash
test -f .env && grep -q APIFY_TOKEN .env || echo "ERROR: 缺少 APIFY_TOKEN，请在 .env 中配置"
```

校验：
- `product` 非空
- `target_market` 非空
- `customer_types` 在合法集合内
- `budget_credits_usd` >0

### Step 1: 展开城市清单 + 推断语言

读取 [`references/city-lists.md`](references/city-lists.md)：

- 输入是国家代码（如 `DE`）→ 取该国 Top `max_cities` 个城市
- 输入是城市（如 `Berlin, Germany`）→ 直接用，不展开
- 输入是大区（如 `Western Europe`）→ 按"大区映射"表展开

读取 [`references/i18n-keywords.md`](references/i18n-keywords.md) 的 "国家 → 默认搜索语言"：

- `DE` → `[de, en]`
- `JP` → `[jp, en]`
- 多语种国家（CH/BE/CA）→ 按城市判断

### Step 2: 翻译产品 + 客户类型

#### 2.1 客户类型翻译
直接查 i18n-keywords.md 的"客户类型 × 语言矩阵"，每语言取前 2 个等义词。

#### 2.2 产品翻译
i18n-keywords.md **不预存行业类目词**，由本 skill 在执行时按目标语言翻译产品名：

- 产品已是英文 → 同时给出 1 个本地语版（用 LLM 翻译，避免太字面）
- 产品是中文 → 给出英文版 + 1 个本地语版

例：`product="硅胶宠物碗"`, `language=de`
→ `["silicone pet bowl", "Silikon Hundenapf", "Silikon Tiernapf"]`

### Step 3: 构造查询计划

```yaml
plan:
  total_estimated_cost_usd: 0.85
  channels:
    google_maps:
      enabled: true
      cities: 5
      queries_per_city: 3       # 按客户类型数
      total_queries: 15
      estimated_cost: 0.50
    google_search:
      enabled: true
      query_templates: [A, B, C]  # 见 search-channels.md
      total_queries: 8
      estimated_cost: 0.12
    facebook_pages:
      enabled: true              # 客户类型含 retailer/brand 时启用
      total_queries: 3
      estimated_cost: 0.15
    contact_enrichment:
      enabled: false             # 默认关
```

如果 `total_estimated_cost_usd > budget_credits_usd`：
- 自动减少 `max_cities` 或 `max_results_per_city`
- 仍超 → 关闭 Facebook 通道
- 仍超 → 报告用户调整预算或缩小范围

### Step 4: 并行执行 3 通道

读取 [`references/search-channels.md`](references/search-channels.md) 的 Actor 输入参数模板。

#### 4.1 Google Maps（每城市每客户类型 1 次调用）

```bash
node --env-file=.env .cursor/skills/apify-ultimate-scraper/reference/scripts/run_actor.js \
  --actor "compass/crawler-google-places" \
  --input '{
    "searchStringsArray": ["Großhändler Tierbedarf in Berlin"],
    "locationQuery": "Berlin, Germany",
    "maxCrawledPlacesPerSearch": 30,
    "language": "de",
    "scrapePlaceDetailPage": true,
    "scrapeContacts": true,
    "skipClosedPlaces": true
  }' \
  --output output/raw/maps_berlin_wholesaler.json \
  --format json
```

#### 4.2 Google Search

```bash
node --env-file=.env .cursor/skills/apify-ultimate-scraper/reference/scripts/run_actor.js \
  --actor "apify/google-search-scraper" \
  --input '{
    "queries": [
      "Großhändler \"Silikon Tiernapf\" site:.de -inurl:alibaba",
      "Vertriebspartner Tierbedarf Silikon"
    ],
    "resultsPerPage": 30,
    "maxPagesPerQuery": 1,
    "languageCode": "de",
    "countryCode": "DE"
  }' \
  --output output/raw/google_de.json \
  --format json
```

#### 4.3 Facebook Pages（仅当 customer_types 含 retailer/brand）

```bash
node --env-file=.env .cursor/skills/apify-ultimate-scraper/reference/scripts/run_actor.js \
  --actor "apify/facebook-search-scraper" \
  --input '{
    "queries": ["Tierbedarf Geschäft Berlin"],
    "searchType": "pages",
    "maxResultsPerQuery": 30,
    "country": "DE"
  }' \
  --output output/raw/fb_berlin.json \
  --format json
```

### Step 5: 合并 + 去重 + 过滤 + 评分

按 search-channels.md "多通道结果合并规则"：

1. **URL 标准化**：统一 https://、去 www、去 trailing /
2. **去重键**：root domain → 公司名（去 GmbH/Inc/Ltd 后缀）→ 电话(E.164)
3. **黑名单过滤**：读 [`references/domain-blacklist.txt`](references/domain-blacklist.txt) + 用户的 `extra_blacklist_domains`
4. **国家校验**：TLD 与 description 提及国家 ≠ 目标国 → confidence 降级
5. **客户类型推断**：从 categories/title/description 文本里匹配关键词，推断 retailer/wholesaler/...
6. **Confidence 评分**：按"多通道命中数 + 有官网 + 国家匹配"打 high/medium/low

### Step 6: Enrichment（默认跳过）

仅当 `enable_enrichment=true`：

```bash
node --env-file=.env .cursor/skills/apify-ultimate-scraper/reference/scripts/run_actor.js \
  --actor "vdrmota/contact-info-scraper" \
  --input '{
    "startUrls": [{"url":"https://acme.de"}, ...],
    "maxDepth": 2,
    "maxRequestsPerStartUrl": 8
  }' \
  --output output/raw/enrich.json \
  --format json
```

把 emails / social 合并回主结果。

### Step 7: 输出

#### 输出文件
- `{output_dir}/leads_{market}_{YYYY-MM-DD}.csv` （Excel 可直接打开）
- `{output_dir}/leads_{market}_{YYYY-MM-DD}.json` （喂下游 skill）

#### 统一 schema（CSV/JSON 一致）

```yaml
- company_name: "ACME Pet Supplies GmbH"
  website: "https://acme-pet.de"
  country: "DE"
  city: "Berlin"
  address: "Hauptstr. 12, 10115 Berlin"
  phone: "+49 30 12345678"
  emails: []                    # Step 6 关闭则为空
  social:
    facebook: "https://facebook.com/acmepet"
    instagram: null
    linkedin: null              # 本 skill 不抓 LinkedIn
  google_rating: 4.7
  reviews_count: 156
  customer_type_guess: "wholesaler"
  source: ["google-maps", "google-search"]
  confidence: high
  next_step: research           # research / skip
  raw_signals:
    - "网站含 'Großhandel' 关键词"
    - "Maps 类目 = Wholesale"
```

#### 摘要报告

```markdown
## 🔍 潜客搜索完成

**目标**: 硅胶宠物碗 → Germany (5 cities)
**用时**: 4 分 32 秒
**成本**: $0.78 / $1.00 budget

### 命中统计
| 通道 | 原始命中 | 黑名单过滤 | 跨通道去重后 |
|---|---|---|---|
| Google Maps | 142 | -8 | 89 |
| Google 搜索 | 78 | -23 | 31 |
| Facebook Pages | 35 | -2 | 18 |
| **合并去重** | - | - | **96 家** |

### Confidence 分布
- 🟢 high: 38 家（research）
- 🟡 medium: 41 家（research）
- 🔴 low: 17 家（skip）

### 客户类型推断分布
- wholesaler: 42
- retailer: 28
- distributor: 14
- 未明: 12

### 下一步
- 📂 名单文件：`output/leads/leads_DE_2026-04-17.csv`
- 🔬 单家深背调：调用 `b2b-customer-research`
- 📥 直接入库：调用 `bitable-trade-customer`
- 🚀 全自动开发：调用 `auto-trade-customer-development`（会复用本次结果）
```

## 错误处理

- **APIFY_TOKEN 无效** → 让用户在 .env 检查 token
- **预算耗尽** → 提示已花费多少，已收集的结果是否要保存
- **目标国不在 city-lists** → 用户提供城市，或回退用 Google 搜索单通道
- **0 命中** → 给出诊断：可能是关键词太窄 / 黑名单太严 / 客户类型不匹配；建议放宽
- **某通道全部失败** → 不中断，仅在报告里标注，其他通道继续

## 注意事项

- 默认**不**做联系人富化（emails 为空），由下游 skill 决定何时调用
- 默认**不**用 LinkedIn 通道，留给 `b2b-customer-research` 单点深背调
- 大型市场（US/JP/DE/IT）建议分两次跑：第一次 max_cities=5 探路，第二次扩到 10
- 结果文件不包含原始 Apify 返回（太大），保留在 `output/raw/`，需要时单独读取
- 涉及个人信息时，对话中只显示样例和数量，不全量回显

## 相关 skill

| Skill | 关系 |
|---|---|
| `apify-ultimate-scraper` | 底层依赖（Actor 调用脚本）|
| `b2b-customer-research` | 下游：单家深背调 |
| `bitable-trade-customer` | 下游：批量入库 |
| `auto-trade-customer-development` | 上游编排：本 skill 是它的"搜索层"|
