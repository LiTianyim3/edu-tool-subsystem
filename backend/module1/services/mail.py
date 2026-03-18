import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, random, string, time
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM     = os.getenv("MAIL_FROM")
MAIL_SERVER   = os.getenv("MAIL_SERVER", "smtp.qq.com")
MAIL_PORT     = int(os.getenv("MAIL_PORT", 465))

EXPIRE_SECONDS = 300
_store: dict[str, tuple[str, float]] = {}

def generate_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

def save_code(email: str, code: str):
    _store[email] = (code, time.time() + EXPIRE_SECONDS)

def verify_code(email: str, code: str) -> bool:
    record = _store.get(email)
    if not record:
        return False
    saved_code, expire_at = record
    if time.time() > expire_at:
        del _store[email]
        return False
    if saved_code != code:
        return False
    del _store[email]
    return True

async def send_reset_code(to_email: str, code: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "【智课助手】密码重置验证码"
    msg["From"]    = MAIL_FROM
    msg["To"]      = to_email
    html = f"""
    <div style="font-family:'PingFang SC',sans-serif;max-width:480px;margin:0 auto;
                padding:32px;background:#f8fafc;border-radius:12px;">
      <h2 style="color:#1e293b;">密码重置验证码</h2>
      <p style="color:#64748b;margin-bottom:24px;">你正在重置智课助手的登录密码，验证码为：</p>
      <div style="background:#2563EB;color:white;font-size:32px;font-weight:bold;
                  letter-spacing:8px;text-align:center;padding:20px;border-radius:10px;">
        {code}
      </div>
      <p style="color:#94a3b8;font-size:13px;margin-top:24px;">验证码 5分钟 内有效，请勿泄露给他人。</p>
    </div>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))
    await aiosmtplib.send(
        msg,
        hostname=MAIL_SERVER,
        port=MAIL_PORT,
        username=MAIL_USERNAME,
        password=MAIL_PASSWORD,
        use_tls=True,
    )