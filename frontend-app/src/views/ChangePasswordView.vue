<template>
  <div class="page-wrap">
    <div class="card">
      <button class="back-btn" @click="router.back()">← 返回</button>
      <h2 class="title">🔒 修改密码</h2>

      <div v-if="successMsg" class="alert success">{{ successMsg }}</div>
      <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>

      <form class="form" @submit.prevent="handleSubmit">
        <div class="field">
          <label>原密码</label>
          <input v-model="form.old_password" type="password" placeholder="请输入原密码" required />
        </div>
        <div class="field">
          <label>新密码</label>
          <input v-model="form.new_password" type="password" placeholder="至少6位" required />
        </div>
        <div class="field">
          <label>确认新密码</label>
          <input v-model="form.confirm_password" type="password" placeholder="再次输入新密码" required />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '提交中...' : '确认修改' }}
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
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const form = reactive({ old_password: '', new_password: '', confirm_password: '' })

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  if (form.new_password !== form.confirm_password) {
    errorMsg.value = '两次输入的新密码不一致'
    return
  }
  if (form.new_password.length < 6) {
    errorMsg.value = '新密码至少6位'
    return
  }
  loading.value = true
  try {
    await authApi.changePassword({ old_password: form.old_password, new_password: form.new_password })
    successMsg.value = '密码修改成功！'
    form.old_password = ''
    form.new_password = ''
    form.confirm_password = ''
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '修改失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4ff;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.card {
  background: #fff;
  border-radius: 20px;
  padding: 44px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 40px rgba(37,99,235,0.10);
}
.back-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 0;
  font-family: inherit;
}
.back-btn:hover { color: #2563EB; }
.title { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 28px; }
.form { display: flex; flex-direction: column; gap: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 14px; color: #374151; font-weight: 500; }
.field input {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}
.field input:focus { border-color: #2563EB; }
.submit-btn {
  margin-top: 6px;
  padding: 14px;
  background: #2563EB;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.submit-btn:hover:not(:disabled) { background: #1d4ed8; }
.submit-btn:disabled { background: #93c5fd; cursor: not-allowed; }
.alert { border-radius: 10px; padding: 12px 16px; font-size: 14px; margin-bottom: 16px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
.alert.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a; }
</style>
