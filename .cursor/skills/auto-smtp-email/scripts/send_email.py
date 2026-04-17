#!/usr/bin/env python3
import argparse
import json
import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


def default_env_file_path() -> Path | None:
    """Skill 目录下 references/credentials.env，存在则作为默认凭证文件。"""
    here = Path(__file__).resolve().parent
    candidate = here.parent / "references" / "credentials.env"
    return candidate if candidate.is_file() else None


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"env 文件不存在: {path}")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value
    return values


def get_config(env_file: str | None) -> dict[str, str]:
    config = dict(os.environ)
    if env_file:
        config.update(load_env_file(Path(env_file)))
    return config


def parse_recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_key_value_pairs(items: list[str] | None) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"模板变量格式错误: {item}，应为 key=value")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"模板变量 key 不能为空: {item}")
        values[key] = value
    return values


def load_template_vars(args: argparse.Namespace) -> dict[str, str]:
    values: dict[str, str] = {}
    if args.vars_file:
        file_values = json.loads(Path(args.vars_file).read_text(encoding="utf-8"))
        if not isinstance(file_values, dict):
            raise ValueError("vars 文件必须是 JSON 对象")
        values.update({str(key): str(value) for key, value in file_values.items()})
    values.update(parse_key_value_pairs(args.var))
    return values


def render_template(content: str, variables: dict[str, str]) -> str:
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_.-]+)\s*}}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return pattern.sub(replace, content)


def read_body(args: argparse.Namespace) -> str:
    if args.body:
        return args.body
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("需要通过 --body、--body-file 或 stdin 提供正文")


def load_signature(args: argparse.Namespace) -> str:
    if args.signature_file:
        return Path(args.signature_file).read_text(encoding="utf-8").strip()
    return ""


def append_signature(body_text: str, signature_text: str) -> str:
    if not signature_text:
        return body_text
    stripped = body_text.rstrip()
    return f"{stripped}\n\n{signature_text}\n"


def build_html_content(args: argparse.Namespace, body_text: str, signature_text: str, template_vars: dict[str, str]) -> str | None:
    if args.html_file:
        html_content = Path(args.html_file).read_text(encoding="utf-8")
        html_with_signature = html_content.replace("{{signature_html}}", signature_text.replace("\n", "<br>\n"))
        return render_template(html_with_signature, template_vars)
    if args.html_template_file:
        template = Path(args.html_template_file).read_text(encoding="utf-8")
        vars_with_defaults = dict(template_vars)
        vars_with_defaults.setdefault("body_text", body_text.replace("\n", "<br>\n"))
        vars_with_defaults.setdefault("signature_html", signature_text.replace("\n", "<br>\n"))
        return render_template(template, vars_with_defaults)
    return None


def load_required_config(config: dict[str, str]) -> dict[str, str]:
    required_keys = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "SMTP_FROM",
        "SMTP_SECURITY",
    ]
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        raise ValueError(f"缺少必填配置: {', '.join(missing)}")

    security = config["SMTP_SECURITY"].strip().lower()
    if security not in {"ssl", "starttls", "none"}:
        raise ValueError("SMTP_SECURITY 仅支持: ssl, starttls, none")

    return {
        "host": config["SMTP_HOST"].strip(),
        "port": config["SMTP_PORT"].strip(),
        "username": config["SMTP_USERNAME"].strip(),
        "password": config["SMTP_PASSWORD"].strip(),
        "from_email": config["SMTP_FROM"].strip(),
        "from_name": config.get("SMTP_FROM_NAME", "").strip(),
        "security": security,
    }


def build_message(
    args: argparse.Namespace,
    config: dict[str, str],
    body_text: str,
    html_content: str | None,
) -> tuple[EmailMessage, list[str]]:
    to_list = parse_recipients(args.to)
    cc_list = parse_recipients(args.cc)
    bcc_list = parse_recipients(args.bcc)
    all_recipients = to_list + cc_list + bcc_list

    if not to_list:
        raise ValueError("至少需要一个收件人: --to")
    if not args.subject:
        raise ValueError("主题不能为空: --subject")

    msg = EmailMessage()
    if config["from_name"]:
        msg["From"] = f'{config["from_name"]} <{config["from_email"]}>'
    else:
        msg["From"] = config["from_email"]
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    if args.reply_to:
        msg["Reply-To"] = args.reply_to
    msg["Subject"] = args.subject

    msg.set_content(body_text, subtype="plain", charset="utf-8")

    if html_content:
        msg.add_alternative(html_content, subtype="html", charset="utf-8")

    return msg, all_recipients


def print_preview(
    args: argparse.Namespace,
    config: dict[str, str],
    recipients: list[str],
    body_text: str,
    signature_text: str,
    html_content: str | None,
) -> None:
    masked_password = "*" * min(len(config["password"]), 8)
    print("=== DRY RUN ===")
    print(f"SMTP Host: {config['host']}")
    print(f"SMTP Port: {config['port']}")
    print(f"SMTP Security: {config['security']}")
    print(f"SMTP Username: {config['username']}")
    print(f"SMTP Password: {masked_password}")
    print(f"From: {config['from_email']}")
    print(f"To: {', '.join(parse_recipients(args.to))}")
    if args.cc:
        print(f"Cc: {args.cc}")
    if args.bcc:
        print(f"Bcc count: {len(parse_recipients(args.bcc))}")
    print(f"Recipients total: {len(recipients)}")
    print(f"Subject: {args.subject}")
    print("--- Body Preview ---")
    print(body_text)
    if signature_text:
        print("--- Signature Preview ---")
        print(signature_text)
    if html_content:
        print("--- HTML Preview ---")
        print(html_content)


def send_message(config: dict[str, str], msg: EmailMessage, recipients: list[str]) -> None:
    port = int(config["port"])
    security_mode = config["security"]

    if security_mode == "ssl":
        with smtplib.SMTP_SSL(config["host"], port, context=ssl.create_default_context()) as server:
            server.login(config["username"], config["password"])
            server.send_message(msg, to_addrs=recipients)
        return

    with smtplib.SMTP(config["host"], port) as server:
        server.ehlo()
        if security_mode == "starttls":
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
        if config["username"] and config["password"]:
            server.login(config["username"], config["password"])
        server.send_message(msg, to_addrs=recipients)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send one email via SMTP")
    parser.add_argument(
        "--env-file",
        help="env 文件路径；省略且存在 skill 内 references/credentials.env 时自动使用该文件",
    )
    parser.add_argument("--to", required=True, help="收件人邮箱，多个用逗号分隔")
    parser.add_argument("--cc", help="抄送邮箱，多个用逗号分隔")
    parser.add_argument("--bcc", help="密送邮箱，多个用逗号分隔")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", help="直接传入纯文本正文")
    parser.add_argument("--body-file", help="从文件读取纯文本正文")
    parser.add_argument("--html-file", help="可选 HTML 正文文件")
    parser.add_argument("--html-template-file", help="HTML 模板文件，支持 {{var}} 占位符")
    parser.add_argument("--signature-file", help="签名文件，将自动追加到正文和 HTML")
    parser.add_argument("--var", action="append", help="模板变量，格式 key=value，可重复传入")
    parser.add_argument("--vars-file", help="模板变量 JSON 文件")
    parser.add_argument("--reply-to", help="可选回复地址")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不发送")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    env_file = args.env_file
    if not env_file:
        default_path = default_env_file_path()
        if default_path is not None:
            env_file = str(default_path)

    try:
        config = load_required_config(get_config(env_file))
        template_vars = load_template_vars(args)
        base_body_text = read_body(args)
        rendered_body_text = render_template(base_body_text, template_vars)
        signature_text = render_template(load_signature(args), template_vars)
        final_body_text = append_signature(rendered_body_text, signature_text)
        html_content = build_html_content(args, rendered_body_text, signature_text, template_vars)
        msg, recipients = build_message(args, config, final_body_text, html_content)

        if args.dry_run:
            print_preview(args, config, recipients, final_body_text, signature_text, html_content)
            return 0

        send_message(config, msg, recipients)
        print(f"邮件发送成功: {', '.join(recipients)}")
        return 0
    except Exception as exc:
        print(f"发送失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
