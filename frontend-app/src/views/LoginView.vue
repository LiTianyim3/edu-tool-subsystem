<template>
  <div class="auth-wrapper">
    <div class="auth-card">

      <div class="brand">
        <span class="brand-icon">📚</span>
        <span class="brand-name">智课助手</span>
      </div>

      <div class="tab-bar">
        <button :class="['tab', { active: mode === 'login' }]" @click="switchMode('login')">登录</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="switchMode('register')">注册</button>
      </div>

      <div class="role-selector">
        <button :class="['role-btn', { active: form.role === 'teacher' }]" @click="form.role = 'teacher'">
          <span>👨‍🏫</span> 教师
        </button>
        <button :class="['role-btn', { active: form.role === 'student' }]" @click="form.role = 'student'">
          <span>👨‍🎓</span> 学生
        </button>
      </div>

      <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

      <!-- 登录表单 -->
      <form v-if="mode === 'login'" class="form" @submit.prevent="handleLogin">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="field">
          <label>
            密码
            <span class="forgot-link" @click="router.push('/forgot-password')">忘记密码？</span>
          </label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-if="mode === 'register'" class="form" @submit.prevent="handleRegister">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="field">
          <label>邮箱 <span class="hint">（用于找回密码）</span></label>
          <input v-model="form.email" type="text" placeholder="请输入邮箱" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="至少6位" required />
        </div>
        <div v-if="form.role === 'student'" class="field">
          <label>学号 <span class="hint">（选填）</span></label>
          <input v-model="form.student_no" type="text" placeholder="请输入学号" />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth.js'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const form = reactive({
  username: '', email: '', password: '',
  role: 'teacher', student_no: '',
})

function switchMode(m) {
  mode.value = m
  errorMsg.value = ''
  successMsg.value = ''
}

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await authApi.login({
      username: form.username,
      password: form.password,
      role: form.role,
    })
    const { access_token, role, username, user_id } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('role', role)
    localStorage.setItem('username', username)
    localStorage.setItem('user_id', user_id)
    router.push(role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  errorMsg.value = ''
  if (form.username.length < 2) { errorMsg.value = '用户名至少2个字符'; return }
  if (form.password.length < 6) { errorMsg.value = '密码至少6位'; return }
  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      email: form.email || '',
      password: form.password,
      role: form.role,
      student_no: form.student_no || undefined,
    })
    successMsg.value = '注册成功！请登录'
    switchMode('login')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 100%);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.auth-card {
  background: #fff;
  border-radius: 20px;
  padding: 44px 40px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 8px 40px rgba(37,99,235,0.10);
}
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 32px; }
.brand-icon { font-size: 28px; }
.brand-name { font-size: 22px; font-weight: 700; color: #1e293b; letter-spacing: 1px; }
.tab-bar { display: flex; border-bottom: 2px solid #e2e8f0; margin-bottom: 24px; }
.tab {
  flex: 1; padding: 10px; border: none; background: none;
  font-size: 15px; color: #94a3b8; cursor: pointer;
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all 0.2s; font-family: inherit;
}
.tab.active { color: #2563EB; border-bottom-color: #2563EB; font-weight: 600; }
.role-selector { display: flex; gap: 12px; margin-bottom: 24px; }
.role-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px; border: 2px solid #e2e8f0; border-radius: 12px;
  background: #f8fafc; font-size: 15px; color: #64748b;
  cursor: pointer; transition: all 0.2s; font-family: inherit;
}
.role-btn.active { border-color: #2563EB; background: #eff6ff; color: #2563EB; font-weight: 600; }
.alert { border-radius: 10px; padding: 12px 16px; font-size: 14px; margin-bottom: 18px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
.alert.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a; }
.form { display: flex; flex-direction: column; gap: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label {
  font-size: 14px; color: #374151; font-weight: 500;
  display: flex; justify-content: space-between; align-items: center;
}
.forgot-link { font-size: 13px; color: #2563EB; cursor: pointer; font-weight: 400; }
.forgot-link:hover { text-decoration: underline; }
.hint { font-size: 12px; color: #94a3b8; font-weight: 400; }
.field input {
  padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 15px; color: #1e293b; outline: none;
  transition: border-color 0.2s; font-family: inherit;
}
.field input:focus { border-color: #2563EB; background: #fafbff; }
.submit-btn {
  margin-top: 6px; padding: 14px; background: #2563EB; color: white;
  border: none; border-radius: 12px; font-size: 16px; font-weight: 600;
  cursor: pointer; letter-spacing: 2px; transition: all 0.2s; font-family: inherit;
}
.submit-btn:hover:not(:disabled) { background: #1d4ed8; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.submit-btn:disabled { background: #93c5fd; cursor: not-allowed; }
</style>