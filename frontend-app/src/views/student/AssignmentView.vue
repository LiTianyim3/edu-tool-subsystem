<template>
  <div class="page">
    <div class="header">
      <div class="header-left">
        <span class="icon">📚</span>
        <span class="title">智课助手 · 学生端</span>
      </div>
      <div class="header-right">
        <span class="welcome">{{ username }}</span>
        <button class="btn-link" @click="router.push('/student/join-class')">加入班级</button>
        <button class="btn-danger" @click="logout">退出</button>
      </div>
    </div>

    <div class="main">
      <div v-if="!hasClass" class="empty-page">
        <div class="empty-icon">🎒</div>
        <p>还没有加入班级</p>
        <button class="btn-primary" @click="router.push('/student/join-class')">加入班级</button>
      </div>

      <template v-else>
        <!-- 班级选择器 -->
        <div class="class-selector" v-if="joinedClasses.length > 1">
          <select v-model="selectedClassIndex" @change="switchClass" class="class-dropdown">
            <option v-for="(c, idx) in joinedClasses" :key="idx" :value="idx">
              {{ c.class_name }} · {{ c.teacher }}
            </option>
          </select>
        </div>
        
        <div class="class-info">班级：{{ classInfo.class_name }} · 教师：{{ classInfo.teacher }}</div>

        <div v-if="assignments.length === 0" class="empty-hint">暂无作业</div>

        <div v-for="a in assignments" :key="a.id" class="assignment-card">
          <div class="assignment-top">
            <span class="assignment-title">{{ a.title }}</span>
            <span :class="['badge', a.submitted ? 'submitted' : isExpired(a.deadline) ? 'expired' : 'active']">
              {{ a.submitted ? '已提交' : isExpired(a.deadline) ? '已截止' : '待提交' }}
            </span>
          </div>
          <div class="assignment-meta">
            截止：{{ formatDate(a.deadline) }} · 满分：{{ a.max_score }}分
            <span v-if="a.is_late" class="late-tag">⚠️ 迟交</span>
          </div>
          <div v-if="a.description" class="assignment-desc">{{ a.description }}</div>

          <div v-if="a.file_path" class="assignment-meta">
            📎 
            <a
              :href="'http://localhost:8000/' + a.file_path.replace(/\\/g, '/')"
              target="_blank"
              style="color:#2563EB"
            >查看作业附件</a>
          </div>
          <!-- 已有分数 -->
          <div v-if="a.final_score !== null" class="score-display">
            得分：<span class="score">{{ a.final_score }}</span> / {{ a.max_score }}
          </div>

          <!-- 上传区域 -->
          <div v-if="!a.submitted && !isExpired(a.deadline)" class="upload-area">
            <input
              :id="'file-' + a.id"
              type="file"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              style="display:none"
              @change="(e) => onFileChange(e, a.id)"
            />
            <label :for="'file-' + a.id" class="file-label">
              {{ selectedFiles[a.id] ? selectedFiles[a.id].name : '点击选择文件（支持PDF/Word/图片）' }}
            </label>
            <button
              class="btn-primary"
              :disabled="!selectedFiles[a.id] || uploading[a.id]"
              @click="submitAssignment(a.id)"
            >
              {{ uploading[a.id] ? '提交中...' : '提交作业' }}
            </button>
          </div>

          <div v-if="uploadErrors[a.id]" class="alert error">{{ uploadErrors[a.id] }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/auth.js'

const router = useRouter()
const username = localStorage.getItem('username')
const assignments = ref([])
const hasClass = ref(false)
const joinedClasses = ref([])
const selectedClassIndex = ref(0)
const classInfo = ref({})
const selectedFiles = reactive({})
const uploading = reactive({})
const uploadErrors = reactive({})

onMounted(async () => {
  try {
    const res = await api.get('/api/v1/classes/joined')
    if (res.data.length > 0) {
      hasClass.value = true
      joinedClasses.value = res.data
      classInfo.value = res.data[0]
      loadAssignments()
    }
  } catch {}
})

async function loadAssignments() {
  const classId = classInfo.value.class_id
  const res = await api.get('/api/v1/assignments/my', {
    params: { class_id: classId }
  })
  assignments.value = res.data
}

function switchClass() {
  classInfo.value = joinedClasses.value[selectedClassIndex.value]
  Object.keys(selectedFiles).forEach(k => delete selectedFiles[k])
  Object.keys(uploadErrors).forEach(k => delete uploadErrors[k])
  loadAssignments()
}

function onFileChange(e, assignmentId) {
  selectedFiles[assignmentId] = e.target.files[0]
  uploadErrors[assignmentId] = ''
}

async function submitAssignment(assignmentId) {
  const file = selectedFiles[assignmentId]
  if (!file) return
  uploading[assignmentId] = true
  uploadErrors[assignmentId] = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    await api.post(`/api/v1/assignments/${assignmentId}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadAssignments()
    delete selectedFiles[assignmentId]
  } catch (err) {
    uploadErrors[assignmentId] = err.response?.data?.detail || '提交失败'
  } finally {
    uploading[assignmentId] = false
  }
}

function logout() { localStorage.clear(); router.push('/login') }
function isExpired(d) { return new Date(d) < new Date() }
function formatDate(d) { return new Date(d).toLocaleString('zh-CN') }
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page { min-height: 100vh; background: #f0fdf4; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
.header { background: #fff; padding: 0 32px; height: 60px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.header-left { display: flex; align-items: center; gap: 10px; }
.icon { font-size: 22px; }
.title { font-size: 17px; font-weight: 700; color: #1e293b; }
.header-right { display: flex; align-items: center; gap: 12px; }
.welcome { font-size: 14px; color: #64748b; }
.main { max-width: 720px; margin: 0 auto; padding: 32px 20px; }
.class-selector { margin-bottom: 16px; }
.class-dropdown { width: 100%; padding: 10px 14px; border: 2px solid #16a34a; border-radius: 10px; font-size: 14px; color: #1e293b; font-family: inherit; cursor: pointer; background: #fff; }
.class-dropdown:focus { outline: none; border-color: #22c55e; }
.class-info { font-size: 14px; color: #64748b; margin-bottom: 20px; background: #fff; padding: 12px 16px; border-radius: 10px; }
.assignment-card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.assignment-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.assignment-title { font-size: 16px; font-weight: 600; color: #1e293b; }
.badge { font-size: 12px; padding: 2px 10px; border-radius: 20px; font-weight: 500; }
.badge.active { background: #eff6ff; color: #2563EB; }
.badge.submitted { background: #dcfce7; color: #16a34a; }
.badge.expired { background: #f1f5f9; color: #94a3b8; }
.assignment-meta { font-size: 13px; color: #64748b; margin-bottom: 8px; }
.late-tag { color: #d97706; margin-left: 8px; }
.assignment-desc { font-size: 13px; color: #475569; background: #f8fafc; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; }
.score-display { font-size: 14px; color: #374151; margin-bottom: 10px; }
.score { font-size: 22px; font-weight: 700; color: #2563EB; }
.upload-area { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.file-label { flex: 1; min-width: 200px; padding: 10px 14px; border: 2px dashed #cbd5e1; border-radius: 10px; font-size: 13px; color: #64748b; cursor: pointer; transition: border-color 0.2s; }
.file-label:hover { border-color: #2563EB; color: #2563EB; }
.empty-page { text-align: center; padding-top: 120px; }
.empty-icon { font-size: 56px; margin-bottom: 16px; }
.empty-page p { font-size: 16px; color: #64748b; margin-bottom: 20px; }
.empty-hint { font-size: 14px; color: #94a3b8; padding: 20px 0; }
.btn-primary { padding: 9px 18px; background: #2563EB; color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-family: inherit; }
.btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }
.btn-link { background: none; border: none; color: #2563EB; font-size: 14px; cursor: pointer; font-family: inherit; }
.btn-danger { padding: 7px 14px; border: none; border-radius: 8px; background: #fee2e2; color: #dc2626; font-size: 13px; cursor: pointer; font-family: inherit; }
.alert { border-radius: 8px; padding: 10px 14px; font-size: 13px; margin-top: 10px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
</style>