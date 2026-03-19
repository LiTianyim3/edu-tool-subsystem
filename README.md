# 教学辅助系统 - 模块1

## 项目结构
```
edu-tool-subsystem/
├── backend/
│   ├── shared/                  # 公共模块（数据库、模型、安全）
│   │   ├── models.py            # 所有数据库表定义
│   │   ├── database.py          # 数据库连接
│   │   └── security.py          # JWT认证与权限
│   ├── module1/                 # 作业管理与认证模块
│   │   ├── routers/             # 路由接口
│   │   │   ├── auth.py          # 认证相关接口
│   │   │   ├── classes.py       # 班级管理接口
│   │   │   └── assignments.py   # 作业管理接口
│   │   ├── schemas/             # 数据校验模型
│   │   └── services/            # 业务逻辑（邮件发送等）
│   ├── uploads/                 # 上传文件存储目录（自动创建）
│   ├── .env                     # 环境变量配置（需修改，不提交Git）
│   ├── requirements.txt
│   └── run.py                   # 启动入口
└── frontend-app/
    ├── src/
    │   ├── api/                 # 接口请求封装
    │   ├── router/              # 路由配置
    │   └── views/
    │       ├── teacher/         # 教师端页面
    │       └── student/         # 学生端页面
    ├── package.json
    └── vite.config.js
```

## 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+

---

## 快速启动

### 1. 配置数据库

打开 `backend/.env`，修改为你本地的数据库配置：
```
DATABASE_URL=mysql+pymysql://你的用户名:你的密码@127.0.0.1:3306/teaching_assistant
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

```

在本地 MySQL 中创建数据库（只需执行一次）：
```sql
CREATE DATABASE teaching_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端
```powershell
cd backend
pip install -r requirements.txt
python run.py
```

启动成功后终端显示：
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

接口文档：`http://localhost:8000/docs`

### 3. 启动前端
```powershell
cd frontend-app
npm install
npm run dev
```

启动成功后访问：`http://localhost:5173`

---

## 已完成功能

**认证模块**
- 教师/学生注册、登录（角色选择）
- 修改密码
- 找回密码（QQ邮箱验证码，5分钟有效）

**班级管理**
- 教师创建班级，自动生成邀请码
- 学生凭邀请码加入班级
- 教师查看班级学生列表

**作业管理**
- 教师发布作业（支持上传附件：PDF/Word/PPT/图片）
- 学生查看作业列表、提交作业（支持上传附件）
- 教师查看所有提交记录、下载学生附件
- 教师手动改分，状态自动更新为"已批改"
- 作业自动判断是否迟交

## 数据库变更记录

> 如果用过周三之前那版的代码，需要执行以下SQL：
```sql
USE teaching_assistant;
-- 2026-03-19：作业表新增附件字段
ALTER TABLE assignments ADD COLUMN file_path VARCHAR(512) NULL;