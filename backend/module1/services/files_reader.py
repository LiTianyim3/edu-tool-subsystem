import os
import base64
from pathlib import Path


def extract_text_from_file(file_path: str) -> dict:
    """
    从文件中提取内容，返回 {"type": "text"/"image", "content": ...}
    text 类型返回文本字符串
    image 类型返回 base64 字符串
    """
    if not file_path or not os.path.exists(file_path):
        return {"type": "text", "content": "（未上传文件）"}

    ext = Path(file_path).suffix.lower()

    # PDF 提取文本
    if ext == ".pdf":
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return {"type": "text", "content": text.strip() or "（PDF内容为空或为扫描件）"}
        except Exception as e:
            return {"type": "text", "content": f"（PDF读取失败：{e}）"}

    # DOCX 提取文本
    elif ext in (".docx", ".doc"):
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return {"type": "text", "content": text or "（文档内容为空）"}
        except Exception as e:
            return {"type": "text", "content": f"（文档读取失败：{e}）"}

    # 图片转 base64
    elif ext in (".jpg", ".jpeg", ".png"):
        try:
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            return {"type": "image", "content": b64, "mime": mime}
        except Exception as e:
            return {"type": "text", "content": f"（图片读取失败：{e}）"}

    else:
        return {"type": "text", "content": f"（不支持的文件类型：{ext}）"}