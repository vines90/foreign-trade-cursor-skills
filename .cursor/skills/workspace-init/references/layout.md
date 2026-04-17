# 工作空间目录结构

本 skill 创建并维护以下目录树。所有目录幂等创建（`mkdir -p`），已存在不动。

```
外贸/                                    项目根
├── .env                                 全局环境变量（APIFY_TOKEN 等）— 用户提供，本 skill 只检测
├── .gitignore                           本 skill 会追加缺失行
│
├── output/                              所有运行时产出
│   ├── leads/                           trade-customer-search 输出潜客名单
│   │   └── leads_{market}_{date}.{json,csv}
│   ├── raw/                             Apify / WebFetch 原始返回（gitignored，体积大）
│   │   └── {actor}_{query}.json
│   ├── research/                        b2b-customer-research 背调报告
│   │   └── {company}_{date}.md
│   ├── emails/                          已发送 / 草稿邮件副本
│   │   ├── drafts/                      未发送的草稿
│   │   └── sent/                        已发出邮件的归档（含 message-id）
│   └── logs/                            运行日志、错误堆栈
│       └── {skill}_{date}.log
│
└── .cursor/
    ├── skills/                          各 skill 定义（已存在，不动）
    ├── state/                           跨 skill 共享状态（gitignored，含 token）
    │   └── bitable.json                 由 bitable-trade-customer 首次 setup 创建
    └── cache/                           可选缓存（gitignored）
        ├── apify/                       Apify 结果缓存
        └── i18n/                        i18n 关键词翻译缓存
```

## 各目录用途说明

### `output/leads/`
- 主要由 `trade-customer-search` 写
- 文件命名：`leads_{ISO_country_code}_{YYYY-MM-DD}.json`
- 同时输出 `.csv` 副本，方便用户在 Excel / 飞书表里过一遍
- 单文件别超 5MB；超了再按城市拆

### `output/raw/`
- 所有 Apify Actor、WebFetch、cursor-ide-browser 的原始返回保留位置
- **必须 gitignore**：体积大、含被搜索人的邮箱手机号等 PII
- 保留 7 天后可手动清理（本 skill 不自动清）

### `output/research/`
- `b2b-customer-research` skill 的背调报告，Markdown 格式
- 文件命名：`{company_slug}_{YYYY-MM-DD}.md`
- **不**要把背调结果只写在飞书 Bitable，本地留一份做版本对比

### `output/emails/sent/`
- 每发一封开发信，把 `subject + body + headers + message-id` 落一份 JSON
- 用于：复盘话术、回查发送历史、给 `bitable-trade-devlog` 做幂等校验

### `output/logs/`
- 任何长流程（auto-trade-customer-development 一次跑 N 家）必须写 log
- 用于事后排查：哪一家挂在哪一步

### `.cursor/state/`
- `bitable.json`：飞书 Bitable 的 `app_token` + 各 `table_id` + 关键 `field_id`，被两个 bitable skill 共享
- 未来可扩展：`smtp_quota.json`、`apify_credit.json` 等

### `.cursor/cache/`
- 完全可选；删掉不影响功能，只影响速度
- 缓存策略由具体 skill 自己决定 TTL，本 skill 只建空壳

## 不在本布局内的东西

下列由其他 skill / 用户自行管理，本 skill 不动：

- `.cursor/skills/*` — 各 skill 自身
- `.cursor/skills/auto-smtp-email/references/credentials.env` — SMTP 凭证（已 gitignore）
- 项目业务文档（公司介绍、产品手册、签名图）建议放在 `assets/` 下，本 skill 不强制
