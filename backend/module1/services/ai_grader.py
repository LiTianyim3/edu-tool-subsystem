import os
import httpx
from dotenv import load_dotenv
# 延迟导入 files_reader，避免启动时的导入/循环依赖问题

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
API_URL = os.getenv("AI_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
AI_MODEL_TEXT = os.getenv("AI_MODEL", "deepseek-ai/DeepSeek-V3")
AI_MODEL_VISION = "Qwen/Qwen2.5-VL-7B-Instruct"  # 处理图片用视觉模型


def _build_messages(
    assignment_title: str,
    assignment_desc: str,
    max_score: int,
    is_late: bool,
    late_score: int,
    teacher_file_content: dict,
    student_file_content: dict,
) -> tuple[list, str]:
    """
    构建发送给大模型的 messages，返回 (messages, model_to_use)
    """
    late_hint = f"\n注意：该作业为迟交，最高得分不超过 {late_score} 分。" if is_late else ""

    system_prompt = f"""你是一位严格但公正的教师，正在批改学生作业。
作业标题：{assignment_title}
作业说明：{assignment_desc or '无'}
满分：{max_score} 分{late_hint}

请综合教师提供的作业要求和学生提交的内容进行评分。
必须严格按照以下 JSON 格式返回，不要有其他内容：
{{"score": 85, "comment": "作业完成较好，结构清晰，但部分细节需要完善。"}}"""

    has_image = (
        teacher_file_content.get("type") == "image" or
        student_file_content.get("type") == "image"
    )

    if not has_image:
        # 纯文本模式
        teacher_text = teacher_file_content.get("content", "（教师未上传附件）")
        student_text = student_file_content.get("content", "（学生未上传作业文件）")

        user_content = f"""【教师上传的作业要求/参考材料】
{teacher_text[:3000]}

【学生提交的作业内容】
{student_text[:4000]}

请根据以上内容评分并给出50-100字的评语。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        return messages, AI_MODEL_TEXT

    else:
        # 含图片，用视觉模型，messages content 改为列表
        user_content = [{"type": "text", "text": system_prompt + "\n\n请根据以下材料批改作业：\n"}]

        # 教师材料
        if teacher_file_content.get("type") == "image":
            user_content.append({"type": "text", "text": "【教师上传的作业要求图片】"})
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{teacher_file_content['mime']};base64,{teacher_file_content['content']}"
                }
            })
        else:
            teacher_text = teacher_file_content.get("content", "（教师未上传附件）")
            user_content.append({"type": "text", "text": f"【教师上传的作业要求】\n{teacher_text[:2000]}"})

        # 学生作业
        if student_file_content.get("type") == "image":
            user_content.append({"type": "text", "text": "\n【学生提交的作业图片】"})
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{student_file_content['mime']};base64,{student_file_content['content']}"
                }
            })
        else:
            student_text = student_file_content.get("content", "（学生未提交文件）")
            user_content.append({"type": "text", "text": f"\n【学生提交的作业内容】\n{student_text[:3000]}"})

        user_content.append({
            "type": "text",
            "text": "\n请评分并给出50-100字评语，严格按JSON格式返回：{\"score\": 85, \"comment\": \"...\"}"
        })

        messages = [{"role": "user", "content": user_content}]
        return messages, AI_MODEL_VISION


async def ai_grade(
    assignment_title: str,
    assignment_desc: str,
    max_score: int,
    is_late: bool,
    late_score: int,
    teacher_file_path: str = "",
    student_file_path: str = "",
) -> dict:
    """调用大模型批改作业，返回 {score, comment}"""

    # 延迟导入并容错：在某些运行环境下顶级导入可能失败或产生循环依赖
    try:
        from module1.services.files_reader import extract_text_from_file
    except Exception:
        extract_text_from_file = lambda p: {"type": "text", "content": "（无法读取文件：解析器未就绪）"}

    teacher_content = extract_text_from_file(teacher_file_path)
    student_content = extract_text_from_file(student_file_path)

    messages, model = _build_messages(
        assignment_title=assignment_title,
        assignment_desc=assignment_desc,
        max_score=max_score,
        is_late=is_late,
        late_score=late_score,
        teacher_file_content=teacher_content,
        student_file_content=student_content,
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(API_URL, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    raw = data["choices"][0]["message"]["content"].strip()

    import json, re
    match = re.search(r'\{.*?\}', raw, re.DOTALL)
    if not match:
        raise ValueError(f"AI 返回格式异常：{raw}")

    result = json.loads(match.group())
    score = max(0, min(int(result["score"]), max_score))
    if is_late:
        score = min(score, late_score)

    return {"score": score, "comment": result["comment"]}