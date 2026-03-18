# edu-tool-subsystem
辅助教学工具子系统
# 教学辅助系统 - 模块1

## 项目结构
```
edu-tool-subsystem/
├── backend/
│   ├── shared/          # 公共模块（数据库、模型、安全）
│   ├── module1/         # 作业管理与认证模块
│   │   ├── routers/     # 路由接口
│   │   ├── schemas/     # 数据校验
│   │   └── services/    # 业务逻辑（邮件等）
│   ├── .env             # 环境变量配置（需修改）
│   ├── requirements.txt
│   └── run.py           # 启动入口
└── frontend-app/
    ├── src/
    │   ├── api/         # 接口封装
    │   ├── router/      # 路由配置
    │   └── views/       # 页面组件
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

打开 `backend/.env`，修改数据库连接为你本地的配置：
```
DATABASE_URL=mysql+pymysql://你的用户名:你的密码@127.0.0.1:3306/teaching_assistant
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

```

然后在本地 MySQL 中创建数据库（只需执行一次）：
```sql
CREATE DATABASE teaching_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端
```powershell
cd backend

# 安装依赖（建议在虚拟环境中执行）
pip install -r requirements.txt

# 启动（会自动创建数据库表）
python run.py
```

启动成功后终端显示：
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

接口文档地址：`http://localhost:8000/docs`

### 3. 启动前端
```powershell
cd frontend-app

# 安装依赖
npm install

# 启动
npm run dev
```

启动成功后访问：`http://localhost:5173`

---

## 已完成功能

- 用户注册（教师/学生角色）
- 用户登录（角色验证）
- 修改密码
- 找回密码（QQ邮箱验证码）

