# 教学辅助系统 - AI 智能批改模块

一个支持 AI 智能批改、作业模板库、多班级管理的教学辅助系统。采用 FastAPI + Vue3 技术栈，集成 DeepSeek V3 模型进行多格式作业评分。

## 核心功能

🎓 **班级与学生管理**
- 教师创建班级、生成邀请码
- 学生加入多个班级、灵活切换视图
- 班级成员管理

📝 **作业发布与提交**
- 教师发布作业（支持 PDF/Word/PPT/图片等附件）
- 自定义评分标准（AI 批改时参考）
- 学生实时提交作业、查看成绩
- 自动迟交判断

🤖 **AI 智能批改**
- 支持多格式文件自动识别：PDF（文本提取）、DOCX（段落提取）、JPG/PNG（图片理解）
- DeepSeek V3 模型智能评分
- 单个或批量批改
- 根据教师的评分标准进行定制化评分
- 自动计算迟交分数上限

📚 **作业模板库**
- 教师保存常用作业为模板（仅保存标题、描述、附件）
- 快速从模板创建新作业（填入截止时间、满分、评分标准即可）
- 模板版本管理

---

## 项目结构

```
edu-tool-subsystem/
├── backend/
│   ├── shared/
│   │   ├── models.py            # SQLAlchemy ORM 模型
│   │   ├── database.py          # 数据库连接与初始化
│   │   └── security.py          # JWT 认证、权限控制
│   ├── module1/
│   │   ├── main.py              # 应用入口
│   │   ├── routers/
│   │   │   ├── auth.py          # 注册、登录、密码重置
│   │   │   ├── classes.py       # 班级创建、加入、查询
│   │   │   └── assignments.py   # 作业发布、提交、批改、模板管理
│   │   ├── schemas/
│   │   │   └── auth.py          # 请求数据验证
│   │   └── services/
│   │       ├── ai_grader.py      # AI 批改核心逻辑
│   │       ├── files_reader.py   # 多格式文件提取
│   │       └── mail.py           # 邮件发送
│   ├── uploads/                 # 用户上传文件存储
│   ├── .env                     # 环境变量（不提交 Git）
│   ├── requirements.txt
│   └── run.py                   # FastAPI 启动脚本
│
└── frontend-app/
    ├── src/
    │   ├── api/
    │   │   └── auth.js          # API 请求封装（自动 JWT 拦截）
    │   ├── router/
    │   │   └── index.js         # Vue Router 路由配置
    │   ├── views/
    │   │   ├── LoginView.vue
    │   │   ├── ChangePasswordView.vue
    │   │   ├── ForgotPasswordView.vue
    │   │   ├── StudentDashboard.vue
    │   │   ├── TeacherDashboard.vue
    │   │   ├── student/
    │   │   │   ├── AssignmentView.vue      # 学生作业列表、提交
    │   │   │   └── JoinClassView.vue       # 加入班级
    │   │   └── teacher/
    │   │       └── AssignmentView.vue      # 教师作业管理、AI 批改
    │   ├── App.vue
    │   └── main.js
    ├── package.json
    └── vite.config.js
```

---

## 环境要求

- **后端**：Python 3.11+
- **前端**：Node.js 18+
- **数据库**：MySQL 8.0+
- **外部服务**：SiliconFlow API（DeepSeek 模型）

---

## 快速启动

### 1. 配置数据库与环境

编辑 `backend/.env`：

```env
# 数据库配置
DATABASE_URL=your_dataset_url

# JWT 认证
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 邮箱配置（找回密码功能）
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-qq-smtp-code
MAIL_FROM=your-email@qq.com
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465

# AI 模型配置（支持多格式文件的 AI 批改）
AI_API_KEY=sk-your-siliconflow-api-key
AI_API_URL=https://api.siliconflow.cn/v1/chat/completions
AI_MODEL=deepseek-ai/DeepSeek-V3
```

<details>
<summary><b>📌 说明</b></summary>

- **DATABASE_URL**：根据实际数据库信息修改
- **MAIL_PASSWORD**：QQ 邮箱需获取 16 位授权码（不是登录密码）
- **AI_API_KEY**：在 https://cloud.siliconflow.cn 注册获取
- 环境变量不提交 Git（`.gitignore` 已配置）

</details>

### 2. 启动后端

```powershell
cd backend
pip install -r requirements.txt
python run.py
```

成功启动标志：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

- 接口文档：http://localhost:8000/docs
- 所有新增表会自动创建（SQLAlchemy `init_db()`）

### 3. 启动前端

```powershell
cd frontend-app
npm install
npm run dev
```

访问：http://localhost:5173

---

## 已实现功能

### ✅ 认证与权限

- 教师/学生注册、登录（角色选择）
- JWT 令牌认证（24 小时有效）
- 修改密码、找回密码（QQ 邮箱验证码）
- 基于角色的访问控制（RBAC）

### ✅ 班级管理

- 教师创建班级、自动生成 6 位邀请码
- 学生凭邀请码加入班级（支持加入多个班级）
- 班级内学生列表、学号管理
- 学生端可切换查看不同班级的作业

### ✅ 作业发布与提交

- 教师发布作业（含标题、描述、附件、截止时间、满分、评分标准）
- 作业自动判断学生是否迟交
- 学生提交作业（支持文件上传）
- 实时查看提交状态（未提交/已提交/已批改）

### ✅ AI 智能批改

**核心能力**
- 支持多格式文件自动识别与提取
  - **PDF**：pdfplumber 文本提取
  - **DOCX**：python-docx 段落提取
  - **JPG/PNG**：Base64 编码传给多模态模型理解
- DeepSeek V3 智能评分（调用 SiliconFlow API）
- 支持单个批改和批量批改
- 根据教师自定义的评分标准进行评分
- 自动限制迟交分数上限

**流程**
1. 教师在发布作业时填写 **"评分标准"**（例如：逻辑清晰 30 分、代码规范 20 分、功能完整 50 分）
2. 学生提交作业
3. 教师点击 **"AI 批改"** 或 **"批量批改"**
4. 系统自动：
   - 提取学生和教师上传的文件内容
   - 将内容、作业描述、评分标准组装成提示词
   - 调用 DeepSeek V3 模型获得评分和评语
   - 保存评分结果到数据库
5. 教师可查看 AI 评分，也可手动修改

### ✅ 作业模板库

**模板包含内容**（设计为可复用的结构）
- 作业标题
- 作业描述/要求
- 附件（参考资料）

**不在模板中**（每次使用时填入）
- 截止时间
- 满分分值
- 评分标准

**使用流程**
1. 教师发布作业后，点击 **"保存为模板"**
2. 下次创建类似作业时，在 **"从模板创建"** 标签页选择
3. 填入新的截止时间、满分、评分标准即可快速发布

### ✅ 成绩管理

- 教师查看所有提交的作业
- 学生查看自己的分数与 AI 评语
- 教师可手动修改评分
- 分数变更实时同步

---

## API 端点（核心）

### 认证模块
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册（teacher/student） |
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/change-password` | 修改密码 |
| POST | `/api/v1/auth/forgot-password/send` | 发送验证码 |
| POST | `/api/v1/auth/forgot-password/reset` | 重置密码 |

### 班级模块
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/classes` | 创建班级 |
| GET | `/api/v1/classes/my` | 查询（教师查自己的班级、学生查加入的班级） |
| POST | `/api/v1/classes/join` | 学生加入班级 |
| GET | `/api/v1/classes/{id}/students` | 查看班级学生列表 |

### 作业模块
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/assignments/` | 发布作业 |
| GET | `/api/v1/assignments/class/{id}` | 获取班级内所有作业（教师用） |
| GET | `/api/v1/assignments/my?class_id=X` | 获取我的作业（学生用，支持按班级筛选） |
| POST | `/api/v1/assignments/submit` | 学生提交作业 |
| GET | `/api/v1/assignments/{id}/submissions` | 获取作业的所有提交（教师用） |
| POST | `/api/v1/assignments/submissions/{id}/ai-grade` | 单个 AI 批改 |
| POST | `/api/v1/assignments/{id}/ai-grade-all` | 批量 AI 批改 |
| PUT | `/api/v1/assignments/submissions/{id}/score` | 手动改分 |

### 模板模块
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/assignments/templates` | 保存作业为模板 |
| GET | `/api/v1/assignments/templates` | 查询自己的模板列表 |
| DELETE | `/api/v1/assignments/templates/{id}` | 删除模板 |
| POST | `/api/v1/assignments/from-template` | 从模板创建作业 |

---

## 数据库模型

### 核心表

**users** - 用户表
```python
id, username, email, hashed_password, role (teacher/student), created_at
```

**classes** - 班级表
```python
id, name, code (邀请码), teacher_id, created_at
```

**student_profiles** - 学生班级映射
```python
id, user_id, class_id, student_no (学号)
```

**assignments** - 作业表
```python
id, class_id, title, description, 
deadline, max_score, 
grading_criteria (评分标准文本),  # ⭐ 新增
file_path (教师附件), created_at
```

**submissions** - 作业提交表
```python
id, assignment_id, student_id, 
file_path (学生文件), is_late, status, submitted_at
```

**ai_grading_results** - AI 评分结果表
```python
id, submission_id, ai_score, ai_comment, model_used, created_at
```

**assignment_templates** - 作业模板表 ⭐ 新增
```python
id, teacher_id, title, description, 
file_path (模板附件), created_at
```

**grading_rules** - 评分规则表（预留，目前通过评分标准文本实现）
```python
id, name, max_score, late_score, quality_tiers (JSON)
```

---

## 数据库迁移说明

### 若从旧版本升级

如果使用过旧版本的代码，需要执行以下操作：

**新增 `grading_criteria` 列**（支持自定义评分标准）
```sql
ALTER TABLE assignments ADD COLUMN grading_criteria LONGTEXT NULL;
```

**或者删除表让系统自动重建**（开发环境）
```sql
DROP TABLE assignments;
DROP TABLE assignment_templates;
-- 重启后端，SQLAlchemy 会自动创建这些表
```

---

## 文件上传限制

- **允许格式**：`.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.ppt`, `.pptx`
- **存储位置**：`backend/uploads/`  
- **文件路径**：`uploads/assignment_{uuid}.{ext}`

---

## 故障排除

### ❌ "Unknown column 'assignments.grading_criteria'"

**原因**：数据库表未更新
**解决**：执行迁移 SQL（见上文）或重建表

### ❌ AI 批改返回 500 错误

**检查**：
1. `.env` 中的 `AI_API_KEY` 是否正确
2. `AI_API_URL` 是否可访问
3. 模型是否支持（目前为 `deepseek-ai/DeepSeek-V3`）

### ❌ 前端 CORS 错误

**已配置**：后端已启用 CORS 中间件，支持 `http://localhost:5173`

---

## 开发规范

- **后端**：FastAPI + SQLAlchemy ORM
- **前端**：Vue3 Composition API + Vite
- **认证**：JWT（Bearer token）
- **API 通信**：RESTful JSON
- **数据库**：MySQL 8.0+

---

## 许可证

MIT License

---

**最后更新**：2026-04-09  
**开发者**：知识工程团队

