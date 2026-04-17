---
name: workspace-init
description: 初始化外贸项目工作空间。幂等创建 output / .cursor/state / .cursor/cache 等运行时目录，补齐 .gitignore 关键忽略项，体检 .env (APIFY_TOKEN)、auto-smtp-email 凭证、bitable 状态等关键配置，并输出 workspace 健康度报告。当用户提到"初始化工作空间"、"init workspace"、"setup workspace"、"创建项目目录"、"工作空间体检"、"项目初始化"、"准备运行环境"时使用。
---

# 工作空间初始化 Skill

## 适用范围

- 第一次拉项目下来，把跑 `auto-trade-customer-development` / `trade-customer-search` / `b2b-customer-research` / `bitable-trade-customer` / `auto-smtp-email` 等 skill 需要的目录全部建好
- 周期性体检：检查必备凭证、状态文件、`.gitignore` 是否完备
- 团队新人 onboarding：一句话把环境跑通

## 不在范围

- 不创建任何业务数据（不会去搜客户、不会建飞书表、不会发邮件）
- 不会覆盖用户已有的配置内容；`.gitignore` 只追加缺失行，不删/不改
- 不调用任何外网 API
- 不写凭证内容；缺凭证时只生成 `.example` 占位 + 提示用户补全

## 幂等保证

所有操作都可以反复跑，不会重复创建、不会破坏已有内容：

- 目录用 `mkdir -p`
- 凭证文件存在则跳过；只在缺失时复制 `.example`
- `.gitignore` 行级去重后只追加新行
- 状态文件 (`.cursor/state/bitable.json`) 不会被本 skill 创建（必须由 `bitable-trade-customer` skill 走完整 setup 才生成）

## 触发即执行

直接跑：

```bash
python3 .cursor/skills/workspace-init/scripts/init.py
```

可选参数：

```bash
python3 .cursor/skills/workspace-init/scripts/init.py --check-only   # 只体检不创建
python3 .cursor/skills/workspace-init/scripts/init.py --verbose       # 输出每个动作
```

执行完后**必须**把脚本输出的 `=== Workspace Status ===` 部分原样展示给用户，让用户看清缺什么。

## 工作流程

### Step 1：建目录

按 [references/layout.md](references/layout.md) 定义的目录树创建（幂等）。核心目录：

```
output/
├── leads/         trade-customer-search 的潜客名单
├── raw/           Apify / WebFetch 原始返回（gitignored）
├── research/      b2b-customer-research 背调报告（Markdown）
├── emails/        发出邮件的副本与草稿
└── logs/          运行时日志、错误堆栈

.cursor/
├── state/         跨 skill 共享状态（如 bitable.json）
└── cache/         可选：apify 结果缓存、查询计划缓存
```

### Step 2：补 .gitignore

确保以下条目存在；缺一行追加一行（不动其他内容）：

- `.env`、`.env.local`、`.env.*.local`
- `.cursor/skills/auto-smtp-email/references/credentials.env`
- `.cursor/state/`（包含 bitable.json 等含 token 的状态）
- `.cursor/cache/`
- `output/raw/`（Apify 原始返回，体积大且常含个人邮箱）
- `node_modules/`、`__pycache__/`、`*.pyc`、`.DS_Store`

完整列表见 [references/gitignore-required.txt](references/gitignore-required.txt)。

### Step 3：体检凭证

依次检查（**只读，不写凭证内容**）：

| 检查项 | 期望 | 缺失时动作 |
|---|---|---|
| `.env` | 存在且包含 `APIFY_TOKEN=apify_api_...` | 提示用户补充，不自动生成 token |
| `.cursor/skills/auto-smtp-email/references/credentials.env` | 存在且包含 `SMTP_HOST/USERNAME/PASSWORD/FROM` | 若不存在，从 `credentials.env.example` 复制一份占位并提示用户填写 |
| `.cursor/state/bitable.json` | 存在且 `app_token` 非空 | 仅警告：`bitable-trade-customer` 首次使用前需走 setup |
| Python 3 | `python3 --version` ≥ 3.10 | 警告但不阻断 |
| Node.js | `node --version` ≥ 18（apify-ultimate-scraper 需要） | 警告但不阻断 |

### Step 4：输出 workspace 状态报告

最终 stdout 必须包含以下格式块，方便 Agent / 用户一眼看清：

```
=== Workspace Status ===
[OK]   directory tree
[OK]   .gitignore
[OK]   .env (APIFY_TOKEN)
[OK]   smtp credentials
[WARN] bitable state not initialized — run bitable-trade-customer setup before storing customers
[OK]   python3 (3.13.x)
[OK]   node (v22.x)

=== Next steps ===
- 跑搜索：调用 trade-customer-search skill
- 入库前：调用 bitable-trade-customer 首次 setup
- 发邮件：auto-smtp-email 已就绪
```

## 与其他 skill 的边界

- 本 skill **只搭骨架**；任何 skill 想读 `output/leads/foo.json` 而文件不在，**不**应该自动调本 skill 去补，应该直接报错让用户处理
- `bitable-trade-customer` 的首次建表（创建飞书 Bitable + 写 `state/bitable.json`）**不在本 skill 范围**，本 skill 只负责检测它有没有
- 凭证内容（SMTP 密码、APIFY token）必须由用户主动给，本 skill 永远不向用户索要凭证

## 典型调用

第一次 onboard：

```
用户：初始化工作空间
Agent：[调用 workspace-init/scripts/init.py，原样回贴 status 输出]
```

定期体检：

```
用户：体检一下项目环境
Agent：[python3 .cursor/skills/workspace-init/scripts/init.py --check-only]
```

CI / Docker AIO 沙箱启动时也可以挂这个脚本做 healthcheck。
