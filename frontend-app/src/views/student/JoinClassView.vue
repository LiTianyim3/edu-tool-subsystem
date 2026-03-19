<template>
  <div class="page-wrap">
    <div class="card">
      <button class="back-btn" @click="router.back()">← 返回</button>
      <h2 class="title">加入班级</h2>

      <div v-if="errorMsg" class="alert error">{{ errorMsg }}</div>
      <div v-if="successMsg" class="alert success">{{ successMsg }}</div>

      <form class="form" @submit.prevent="handleJoin">
        <div class="field">
          <label>班级邀请码</label>
          <input v-model="form.class_code" type="text" placeholder="请输入教师提供的邀请码" required />
        </div>
        <div class="field">
          <label>学号</label>
          <input v-model="form.student_no" type="text" placeholder="请输入学号" required />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '加入中...' : '加入班级' }}
        </button>
      </form>

      <div v-if="joinedClasses.length" class="joined-list">
        <h3>已加入的班级</h3>
        <div v-for="c in joinedClasses" :key="c.class_id" class="class-item">
          <div class="class-name">{{ c.class_name }}</div>
          <div class="class-meta">教师：{{ c.teacher }} · 学号：{{ c.student_no }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/auth.js'

const router = useRouter()
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const joinedClasses = ref([])

const form = reactive({ class_code: '', student_no: '' })

onMounted(async () => {
  try {
    const res = await api.get('/api/v1/classes/joined')
    joinedClasses.value = res.data
  } catch {}
})

async function handleJoin() {
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await api.post('/api/v1/classes/join', form)
    successMsg.value = res.data.message
    form.class_code = ''
    form.student_no = ''
    const res2 = await api.get('/api/v1/classes/joined')
    joinedClasses.value = res2.data
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '加入失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page-wrap {
  min-height: 100vh; display: flex; justify-content: center; padding: 40px 20px;
  background: #f0f4ff; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.card {
  background: #fff; border-radius: 20px; padding: 40px;
  width: 100%; max-width: 480px; height: fit-content;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}
.back-btn { background: none; border: none; color: #64748b; font-size: 14px; cursor: pointer; margin-bottom: 20px; padding: 0; font-family: inherit; }
.back-btn:hover { color: #2563EB; }
.title { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 28px; }
.alert { border-radius: 10px; padding: 12px 16px; font-size: 14px; margin-bottom: 18px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
.alert.success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a; }
.form { display: flex; flex-direction: column; gap: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 14px; color: #374151; font-weight: 500; }
.field input { padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 10px; font-size: 15px; outline: none; transition: border-color 0.2s; font-family: inherit; }
.field input:focus { border-color: #2563EB; }
.submit-btn { margin-top: 6px; padding: 14px; background: #2563EB; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all 0.2s; }
.submit-btn:hover:not(:disabled) { background: #1d4ed8; }
.submit-btn:disabled { background: #93c5fd; cursor: not-allowed; }
.joined-list { margin-top: 32px; }
.joined-list h3 { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 12px; }
.class-item { background: #f8fafc; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
.class-name { font-size: 15px; font-weight: 500; color: #1e293b; }
.class-meta { font-size: 13px; color: #64748b; margin-top: 4px; }
</style>