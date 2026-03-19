<template>
  <div class="page">
    <div class="header">
      <div class="header-left">
        <span class="icon">📚</span>
        <span class="title">智课助手 · 教师端</span>
      </div>
      <div class="header-right">
        <span class="welcome">{{ username }}</span>
        <button class="btn-danger" @click="logout">退出</button>
      </div>
    </div>

    <div class="main">
      <div class="sidebar">
        <div class="sidebar-title">
          我的班级
          <button class="btn-add" @click="showCreateClass = true">+ 新建</button>
        </div>
        <div
          v-for="c in classes" :key="c.id"
          :class="['class-item', { active: selectedClass?.id === c.id }]"
          @click="selectClass(c)"
        >
          <div class="class-name">{{ c.name }}</div>
          <div class="class-meta">{{ c.student_count }}人 · 邀请码：{{ c.code }}</div>
        </div>
        <div v-if="classes.length === 0" class="empty-hint">暂无班级，点击新建</div>
      </div>

      <div class="content">
        <template v-if="selectedClass">
          <div class="content-header">
            <span class="content-title">{{ selectedClass.name }} · 作业列表</span>
            <button class="btn-primary" @click="showCreateAssignment = true">+ 发布作业</button>
          </div>

          <div v-if="assignments.length === 0" class="empty-hint">暂无作业，点击发布</div>

          <div v-for="a in assignments" :key="a.id" class="assignment-card">
            <div class="assignment-top">
              <span class="assignment-title">{{ a.title }}</span>
              <span :class="['badge', isExpired(a.deadline) ? 'expired' : 'active']">
                {{ isExpired(a.deadline) ? '已截止' : '进行中' }}
              </span>
            </div>
            <div class="assignment-meta">
              截止：{{ formatDate(a.deadline) }} ·
              满分：{{ a.max_score }}分 ·
              提交：{{ a.submission_count }}人
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
            <div class="assignment-actions">
              <button class="btn-outline" @click="viewSubmissions(a)">查看提交</button>
            </div>
          </div>
        </template>

        <div v-else class="empty-hint center">← 选择左侧班级查看作业</div>
      </div>
    </div>

    <!-- 提交列表弹窗 -->
    <div v-if="showSubmissions" class="modal-mask" @click.self="showSubmissions = false">
      <div class="modal">
        <div class="modal-header">
          <span>{{ currentAssignment?.title }} · 提交情况</span>
          <button class="close-btn" @click="showSubmissions = false">✕</button>
        </div>
        <div v-if="submissions.length === 0" class="empty-hint">暂无学生提交</div>
        <table v-else class="sub-table">
          <thead>
            <tr>
              <th>学生</th>
              <th>学号</th>
              <th>附件</th>
              <th>提交时间</th>
              <th>迟交</th>
              <th>状态</th>
              <th>分数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in submissions" :key="s.submission_id">
              <td>{{ s.student_name }}</td>
              <td>{{ s.student_no }}</td>
              <td>
                <template v-if="s.file_path">
                  <a
                    :href="'http://localhost:8000/' + s.file_path.replace(/\\/g, '/')"
                    target="_blank"
                    class="btn-sm file-link"
                  >查看文件</a>
                </template>
                <span v-else style="color:#94a3b8">无附件</span>
              </td>
              <td>{{ formatDate(s.submitted_at) }}</td>
              <td>{{ s.is_late ? '⚠️ 是' : '否' }}</td>
              <td>{{ statusLabel(s.status) }}</td>
              <td>
                <input
                  v-if="editingId === s.submission_id"
                  v-model="editScore"
                  type="number" style="width:60px"
                />
                <span v-else>{{ s.final_score ?? '-' }}</span>
              </td>
              <td>
                <button v-if="editingId !== s.submission_id" class="btn-sm" @click="startEdit(s)">改分</button>
                <button v-else class="btn-sm green" @click="saveScore(s.submission_id)">保存</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新建班级弹窗 -->
    <div v-if="showCreateClass" class="modal-mask" @click.self="showCreateClass = false">
      <div class="modal small">
        <div class="modal-header">
          <span>新建班级</span>
          <button class="close-btn" @click="showCreateClass = false">✕</button>
        </div>
        <div v-if="classError" class="alert error">{{ classError }}</div>
        <div class="field">
          <label>班级名称</label>
          <input v-model="newClassName" type="text" placeholder="如：计算机2101班" />
        </div>
        <button class="btn-primary full" @click="createClass" :disabled="classLoading">
          {{ classLoading ? '创建中...' : '确认创建' }}
        </button>
      </div>
    </div>

    <!-- 发布作业弹窗 -->
    <div v-if="showCreateAssignment" class="modal-mask" @click.self="showCreateAssignment = false">
      <div class="modal small">
        <div class="modal-header">
          <span>发布作业</span>
          <button class="close-btn" @click="showCreateAssignment = false">✕</button>
        </div>
        <div v-if="assignmentError" class="alert error">{{ assignmentError }}</div>
        <div class="field">
          <label>作业标题</label>
          <input v-model="newAssignment.title" type="text" placeholder="请输入作业标题" />
        </div>
        <div class="field">
          <label>作业描述（选填）</label>
          <textarea v-model="newAssignment.description" placeholder="作业要求说明..." rows="3"></textarea>
        </div>
        <div class="field">
          <label>截止时间</label>
          <input v-model="newAssignment.deadline" type="datetime-local" />
        </div>
        <div class="field">
          <label>满分分值</label>
          <input v-model="newAssignment.max_score" type="number" min="1" max="100" />
        </div>
        <div class="field">
          <label>附件（选填）</label>
          <input
            id="assignment-file"
            type="file"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.ppt,.pptx"
            style="display:none"
            @change="onAssignmentFileChange"
          />
          <label for="assignment-file" class="file-label">
            {{ assignmentFile ? assignmentFile.name : '点击上传附件（PDF/Word/PPT/图片）' }}
          </label>
        </div>
        <button class="btn-primary full" @click="createAssignment" :disabled="assignmentLoading">
          {{ assignmentLoading ? '发布中...' : '确认发布' }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/auth.js'

const router = useRouter()
const username = localStorage.getItem('username')

const classes = ref([])
const selectedClass = ref(null)
const assignments = ref([])
const submissions = ref([])
const currentAssignment = ref(null)

const showCreateClass = ref(false)
const showCreateAssignment = ref(false)
const showSubmissions = ref(false)

const newClassName = ref('')
const classError = ref('')
const classLoading = ref(false)

const newAssignment = reactive({ title: '', description: '', deadline: '', max_score: 100 })
const assignmentError = ref('')
const assignmentLoading = ref(false)
const assignmentFile = ref(null)

const editingId = ref(null)
const editScore = ref(0)

onMounted(loadClasses)

async function loadClasses() {
  const res = await api.get('/api/v1/classes/my')
  classes.value = res.data
}

async function selectClass(c) {
  selectedClass.value = c
  const res = await api.get(`/api/v1/assignments/class/${c.id}`)
  assignments.value = res.data
}

async function createClass() {
  classError.value = ''
  if (!newClassName.value.trim()) { classError.value = '请输入班级名称'; return }
  classLoading.value = true
  try {
    await api.post('/api/v1/classes/', { name: newClassName.value })
    showCreateClass.value = false
    newClassName.value = ''
    await loadClasses()
  } catch (err) {
    classError.value = err.response?.data?.detail || '创建失败'
  } finally {
    classLoading.value = false
  }
}

function onAssignmentFileChange(e) {
  assignmentFile.value = e.target.files[0]
}

async function createAssignment() {
  assignmentError.value = ''
  if (!newAssignment.title) { assignmentError.value = '请填写标题'; return }
  if (!newAssignment.deadline) { assignmentError.value = '请选择截止时间'; return }
  assignmentLoading.value = true
  try {
    const formData = new FormData()
    formData.append('class_id', selectedClass.value.id)
    formData.append('title', newAssignment.title)
    formData.append('description', newAssignment.description || '')
    formData.append('deadline', new Date(newAssignment.deadline).toISOString())
    formData.append('max_score', newAssignment.max_score)
    if (assignmentFile.value) {
      formData.append('file', assignmentFile.value)
    }
    await api.post('/api/v1/assignments/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showCreateAssignment.value = false
    assignmentFile.value = null
    Object.assign(newAssignment, { title: '', description: '', deadline: '', max_score: 100 })
    await selectClass(selectedClass.value)
  } catch (err) {
    assignmentError.value = err.response?.data?.detail || '发布失败'
  } finally {
    assignmentLoading.value = false
  }
}

async function viewSubmissions(a) {
  currentAssignment.value = a
  const res = await api.get(`/api/v1/assignments/${a.id}/submissions`)
  submissions.value = res.data
  showSubmissions.value = true
}

function startEdit(s) {
  editingId.value = s.submission_id
  editScore.value = s.final_score ?? 0
}

async function saveScore(id) {
  await api.put(`/api/v1/assignments/submissions/${id}/score`, { final_score: Number(editScore.value) })
  editingId.value = null
  await viewSubmissions(currentAssignment.value)
}

function logout() { localStorage.clear(); router.push('/login') }
function isExpired(d) { return new Date(d) < new Date() }
function formatDate(d) { return new Date(d).toLocaleString('zh-CN') }
function statusLabel(s) {
  return { pending: '待批改', ai_grading: 'AI批改中', ai_done: 'AI完成', teacher_reviewed: '已批改' }[s] || s
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page { min-height: 100vh; background: #f0f4ff; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
.header { background: #fff; padding: 0 32px; height: 60px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.header-left { display: flex; align-items: center; gap: 10px; }
.icon { font-size: 22px; }
.title { font-size: 17px; font-weight: 700; color: #1e293b; }
.header-right { display: flex; align-items: center; gap: 12px; }
.welcome { font-size: 14px; color: #64748b; }
.main { display: flex; height: calc(100vh - 60px); }
.sidebar { width: 260px; background: #fff; border-right: 1px solid #e2e8f0; padding: 20px 16px; overflow-y: auto; }
.sidebar-title { font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.class-item { padding: 12px; border-radius: 10px; cursor: pointer; margin-bottom: 8px; transition: all 0.2s; border: 1.5px solid transparent; }
.class-item:hover { background: #f8fafc; }
.class-item.active { background: #eff6ff; border-color: #2563EB; }
.class-name { font-size: 14px; font-weight: 500; color: #1e293b; }
.class-meta { font-size: 12px; color: #94a3b8; margin-top: 3px; }
.content { flex: 1; padding: 24px; overflow-y: auto; }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.content-title { font-size: 17px; font-weight: 600; color: #1e293b; }
.assignment-card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.assignment-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.assignment-title { font-size: 16px; font-weight: 600; color: #1e293b; }
.badge { font-size: 12px; padding: 2px 10px; border-radius: 20px; font-weight: 500; }
.badge.active { background: #dcfce7; color: #16a34a; }
.badge.expired { background: #f1f5f9; color: #94a3b8; }
.assignment-meta { font-size: 13px; color: #64748b; margin-bottom: 6px; }
.assignment-desc { font-size: 13px; color: #475569; background: #f8fafc; padding: 8px 12px; border-radius: 8px; margin-bottom: 10px; }
.assignment-actions { display: flex; gap: 8px; }
.empty-hint { font-size: 14px; color: #94a3b8; padding: 20px 0; }
.empty-hint.center { text-align: center; padding-top: 100px; }
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; border-radius: 16px; padding: 28px; width: 90%; max-width: 720px; max-height: 80vh; overflow-y: auto; }
.modal.small { max-width: 440px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-size: 16px; font-weight: 600; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; color: #94a3b8; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.field label { font-size: 14px; color: #374151; font-weight: 500; }
.field input, .field textarea { padding: 10px 14px; border: 2px solid #e2e8f0; border-radius: 10px; font-size: 14px; outline: none; font-family: inherit; transition: border-color 0.2s; }
.field input:focus, .field textarea:focus { border-color: #2563EB; }
.sub-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.sub-table th { background: #f8fafc; padding: 10px 12px; text-align: left; color: #374151; font-weight: 500; }
.sub-table td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #475569; }
.btn-primary { padding: 9px 18px; background: #2563EB; color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-family: inherit; }
.btn-primary:hover { background: #1d4ed8; }
.btn-primary.full { width: 100%; padding: 12px; font-size: 15px; }
.btn-outline { padding: 7px 14px; border: 1.5px solid #2563EB; border-radius: 8px; background: none; color: #2563EB; font-size: 13px; cursor: pointer; font-family: inherit; }
.btn-add { padding: 4px 10px; background: #eff6ff; border: 1.5px solid #2563EB; border-radius: 6px; color: #2563EB; font-size: 12px; cursor: pointer; font-family: inherit; }
.btn-danger { padding: 7px 14px; border: none; border-radius: 8px; background: #fee2e2; color: #dc2626; font-size: 13px; cursor: pointer; font-family: inherit; }
.btn-sm { padding: 4px 10px; border: 1.5px solid #e2e8f0; border-radius: 6px; background: none; color: #475569; font-size: 12px; cursor: pointer; font-family: inherit; }
.btn-sm.green { border-color: #16a34a; color: #16a34a; }
.file-link { color: #2563EB; border-color: #2563EB; text-decoration: none; display: inline-block; }
.file-link:hover { background: #eff6ff; }
.file-label { display: block; padding: 10px 14px; border: 2px dashed #cbd5e1; border-radius: 10px; font-size: 13px; color: #64748b; cursor: pointer; transition: border-color 0.2s; }
.file-label:hover { border-color: #2563EB; color: #2563EB; }
.alert { border-radius: 8px; padding: 10px 14px; font-size: 13px; margin-bottom: 14px; }
.alert.error { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; }
</style>