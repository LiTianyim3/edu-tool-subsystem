from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.database import init_db
from module1.routers import auth

app = FastAPI(title="教学辅助系统 - 模块1", version="1.0.0")

# 允许前端跨域（开发阶段放开所有，上线后改为具体域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)

@app.on_event("startup")
def startup():
    init_db()   # 自动创建数据库表

@app.get("/")
def root():
    return {"message": "模块1 API 运行中"}
