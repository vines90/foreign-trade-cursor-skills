# 配置说明

## Agent 执行顺序（避免误读 example）

- 在 **DeerFlow** 中，若项目根目录 **`.env`** 已配置 `SMTP_*`（由 `serve.sh` 加载），执行 `python3 .../scripts/send_email.py` 时**进程环境已含凭证**，无需先 `read_file` `credentials.env`；也**勿**因读不到 gitignore 文件就向用户索要授权码。
- **优先**确认发信命令能跑通（可先 `--dry-run`）；若环境变量不足，再检查 `references/credentials.env`。
- **`credentials.env.example` 仅为模板**，用于说明变量名与示例占位符。

## env 文件格式

推荐在本 skill 目录下创建 `references/credentials.env`，内容可参考：

```dotenv
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USERNAME=your_account@163.com
SMTP_PASSWORD=your_smtp_authorization_code
SMTP_FROM=your_account@163.com
SMTP_FROM_NAME=Your Name
SMTP_SECURITY=ssl
```

## 字段说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `SMTP_HOST` | 是 | SMTP 服务器地址，如 `smtp.163.com` |
| `SMTP_PORT` | 是 | SMTP 端口，如 `465` |
| `SMTP_USERNAME` | 是 | SMTP 登录账号 |
| `SMTP_PASSWORD` | 是 | SMTP 密码或授权码 |
| `SMTP_FROM` | 是 | 发件人邮箱地址 |
| `SMTP_FROM_NAME` | 否 | 发件人显示名称 |
| `SMTP_SECURITY` | 是 | `ssl`、`starttls`、`none` 之一 |

## 常见安全模式

- `ssl`: 连接建立时直接走 SSL，常见于 `465`
- `starttls`: 先普通连接，再升级为 TLS，常见于 `587`
- `none`: 不加密，不推荐

## 163 邮箱建议

- 服务器：`smtp.163.com`
- 优先尝试端口：`465`
- 安全模式：`ssl`
- 密码字段通常填 SMTP 授权码，不是网页登录密码

## 脚本参数

```bash
python3 scripts/send_email.py --help
```

支持的核心参数：

- `--env-file`: 指定 env 文件路径
- `--to`: 收件人，多个邮箱用逗号分隔
- `--cc`: 抄送，多个邮箱用逗号分隔
- `--bcc`: 密送，多个邮箱用逗号分隔
- `--subject`: 邮件主题
- `--body`: 直接传入纯文本正文
- `--body-file`: 从文件读取纯文本正文
- `--html-file`: 可选，发送 HTML 正文
- `--html-template-file`: HTML 模板文件，支持 `{{var}}` 占位符
- `--signature-file`: 从文件读取签名，自动追加到正文和 HTML
- `--var`: 传入模板变量，格式 `key=value`
- `--vars-file`: JSON 格式模板变量文件
- `--reply-to`: 可选，回复地址
- `--dry-run`: 只检查并预览，不发送

## 签名文件

推荐单独维护一个 UTF-8 文本文件，例如：

```text
Best regards,
Liyang
SlashBeyond
Email: aislash@163.com
```

发送时通过 `--signature-file` 追加到纯文本正文；若同时使用 HTML 模板，脚本会自动生成 `signature_html` 变量。

## HTML 模板

推荐使用 `--html-template-file`，模板支持 `{{name}}` 这种占位符。

示例：

```html
<html>
  <body>
    <p>Hello {{company_name}},</p>
    <p>{{body_text}}</p>
    <p>{{signature_html}}</p>
  </body>
</html>
```

模板变量来源：

- 命令行 `--var key=value`
- `--vars-file` 指向的 JSON 文件

若变量缺失，占位符会保留原样，方便排查。

## 推荐工作方式

1. 先整理好邮件主题和正文
2. 先执行一次 `--dry-run`
3. 确认无误后再真实发送

推荐在正式发送前检查：

- 收件人和抄送是否正确
- 签名文件是否为最新版本
- HTML 模板里的占位符是否都已替换

## 常见错误排查

### 认证失败

- 检查是否开启了 SMTP 服务
- 检查是否使用了授权码而不是网页登录密码
- 检查账号是否被风控限制

### 连接失败

- 检查 `SMTP_HOST`、`SMTP_PORT`、`SMTP_SECURITY`
- 检查本机网络是否拦截对应端口

### 邮件乱码

- 脚本默认使用 UTF-8
- 正文文件请保存为 UTF-8 编码
