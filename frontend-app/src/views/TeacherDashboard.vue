<template>
  <div class="dashboard">
    <div class="header">
      <div class="header-left">
        <span class="icon">📚</span>
        <span class="title">智课助手 · 教师端</span>
      </div>
      <div class="header-right">
        <span class="welcome">你好，{{ username }} 👋</span>
        <button class="btn-outline" @click="goChangePwd">修改密码</button>
        <button class="btn-danger" @click="logout">退出登录</button>
      </div>
    </div>
    <div class="content">
      <div class="card">
        <div class="card-icon">✅</div>
        <h2>登录成功！</h2>
        <p>教师端功能开发中，后续将在此页面添加：</p>
        <ul>
          <li>📝 作业发布与管理</li>
          <li>🤖 AI 智能批改</li>
          <li>📊 成绩统计与可视化</li>
          <li>👥 班级管理</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username') || '教师'

function logout() {
  localStorage.clear()
  router.push('/login')
}
function goChangePwd() {
  router.push('/change-password')
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }

.dashboard { min-height: 100vh; background: #f0f4ff; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }

.header {
  background: #fff;
  padding: 0 40px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.header-left { display: flex; align-items: center; gap: 10px; }
.icon { font-size: 24px; }
.title { font-size: 18px; font-weight: 700; color: #1e293b; }
.header-right { display: flex; align-items: center; gap: 12px; }
.welcome { font-size: 14px; color: #64748b; }

.btn-outline {
  padding: 7px 16px;
  border: 1.5px solid #2563EB;
  border-radius: 8px;
  background: none;
  color: #2563EB;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
}
.btn-danger {
  padding: 7px 16px;
  border: none;
  border-radius: 8px;
  background: #fee2e2;
  color: #dc2626;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
}

.content { display: flex; align-items: center; justify-content: center; padding: 60px 20px; }

.card {
  background: #fff;
  border-radius: 20px;
  padding: 48px 56px;
  text-align: center;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
  max-width: 480px;
  width: 100%;
}
.card-icon { font-size: 56px; margin-bottom: 20px; }
.card h2 { font-size: 24px; color: #1e293b; margin-bottom: 16px; }
.card p { font-size: 15px; color: #64748b; margin-bottom: 20px; }
.card ul { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.card ul li { font-size: 15px; color: #475569; background: #f8fafc; border-radius: 8px; padding: 10px 16px; }
</style>
