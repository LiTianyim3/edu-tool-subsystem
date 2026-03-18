<template>
  <div class="page-wrap">
    <div class="card">
      <button class="back-btn" @click="router.push('/login')">← 返回登录</button>
      <h2 class="title">🔑 找回密码</h2>

      <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

      <!-- 第一步：输入邮箱获取验证码 -->
      <template v-if="step === 1">
        <p class="desc">请输入注册时使用的邮箱，验证码将发送到该邮箱。</p>
        <div class="field">
          <label>邮箱</label>
          <div class="input-row">
            <input v-model="email" type="text" placeholder="请输入注册邮箱" />
            <button class="code-btn" @click="sendCode" :disabled="countdown > 0 || sending">
              {{ countdown > 0 ? `${countdown}s 后重发` : (sending ? '发送中...' : '发送验证码') }}
            </button>
          </div>
        </div>
        <div class="field mt">
          <label>验证码</label>
          <input v-model="code" type="text" placeholder="请输入6位验证码" maxlength="6" />
        </div>
        <button class="submit-btn" @click="goNextStep" :disabled="!email || code.length !== 6">
          下一步
        </button>
      </template>

      <!-- 第二步：设置新密码 -->
      <template v-if="step === 2">
        <p class="desc">验证通过！请设置你的新密码。</p>
        <div class="field">
          <label>新密码</label>
          <input v-model="newPassword" type="password" placeholder="至少6位" />
        </div>
        <div class="field mt">
          <label>确认新密码</label>
          <input v-model="confirmPassword" type="password" placeholder="再次输入新密码" />
        </div>
        <button class="submit-btn" @click="resetPassword" :disabled="loading">
          {{ loading ? '提交中...' : '确认重置密码' }}
        </button>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth.js'

const router = useRouter()
const step = ref(1)
const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const sending = ref(false)
const loading = ref(false)
const countdown = ref(0)

let timer = null

function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
}

async function sendCode() {
  if (!email.value) { errorMsg.value = '请输入邮箱'; return }
  errorMsg.value = ''
  sending.value = true
  try {
    await authApi.sendResetCode({ email: email.value })
    successMsg.value = '验证码已发送，请查收邮件（注意检查垃圾箱）'
    startCountdown()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '发送失败，请确认邮箱是否正确'
  } finally {
    sending.value = false
  }
}

function goNextStep() {
  if (code.value.length !== 6) { errorMsg.value = '请输入6位验证码'; return }
  errorMsg.value = ''
  successMsg.value = ''
  step.value = 2
}

async function resetPassword() {
  errorMsg.value = ''
  if (newPassword.value.length < 6) { errorMsg.value = '新密码至少6位'; return }
  if (newPassword.value !== confirmPassword.value) { errorMsg.value = '两次密码输入不一致'; return }
  loading.value = true
  try {
    await authApi.resetPassword({
      email: email.value,
      code: code.value,
      new_password: newPassword.value,
    })
    successMsg.value = '密码重置成功！3秒后跳转到登录页...'
    setTimeout(() => router.push('/login'), 3000)
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '重置失败，验证码可能已过期，请重新获取'
    step.value = 1
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page-wrap {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 100%);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.card {
  background: #fff; border-radius: 20px; padding: 44px 40px;
  width: 100%; max-width: 440px;
  box-shadow: 0 8px 40px rgba(37,99,235,0.10);
}
.back-btn {
  background: none; border: none; color: #64748b; font-size: 14px;
  cursor: pointer; margin-bottom: 20px; padding: 0; font-family: inherit;
}
.back-btn:hover { color: #2563EB; }
.title { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 12px; }
.desc { font-size: 14px; color: #64748b; margin-bottom: 24px; line-height: 1.6; }
.alert { border-radius: 10px; padding: 12px 16px; font-size: 14px; margin-bottom: 18px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
.alert.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.mt { margin-top: 16px; }
.field label { font-size: 14px; color: #374151; font-weight: 500; }
.field input {
  padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 10px;
  font-size: 15px; outline: none; transition: border-color 0.2s; font-family: inherit;
}
.field input:focus { border-color: #2563EB; }
.input-row { display: flex; gap: 10px; }
.input-row input { flex: 1; }
.code-btn {
  padding: 0 16px; background: #eff6ff; border: 2px solid #2563EB;
  border-radius: 10px; color: #2563EB; font-size: 13px; font-weight: 500;
  cursor: pointer; white-space: nowrap; font-family: inherit; transition: all 0.2s;
}
.code-btn:hover:not(:disabled) { background: #2563EB; color: white; }
.code-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.submit-btn {
  margin-top: 28px; width: 100%; padding: 14px; background: #2563EB; color: white;
  border: none; border-radius: 12px; font-size: 16px; font-weight: 600;
  cursor: pointer; letter-spacing: 1px; transition: all 0.2s; font-family: inherit;
}
.submit-btn:hover:not(:disabled) { background: #1d4ed8; }
.submit-btn:disabled { background: #93c5fd; cursor: not-allowed; }
</style>