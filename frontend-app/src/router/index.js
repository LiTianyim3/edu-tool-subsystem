import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import ChangePasswordView from '@/views/ChangePasswordView.vue'
import TeacherDashboard from '@/views/TeacherDashboard.vue'
import StudentDashboard from '@/views/StudentDashboard.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import JoinClassView from '@/views/student/JoinClassView.vue'
import TeacherAssignmentView from '@/views/teacher/AssignmentView.vue'
import StudentAssignmentView from '@/views/student/AssignmentView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/forgot-password', component: ForgotPasswordView },
  { path: '/change-password', component: ChangePasswordView, meta: { requiresAuth: true } },
  { path: '/teacher/dashboard', component: TeacherDashboard, meta: { requiresAuth: true, role: 'teacher' } },
  { path: '/student/dashboard', component: StudentDashboard, meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/join-class', component: JoinClassView, meta: { requiresAuth: true, role: 'student' } },
  { path: '/teacher/assignments', component: TeacherAssignmentView, meta: { requiresAuth: true, role: 'teacher' } },
{ path: '/student/assignments', component: StudentAssignmentView, meta: { requiresAuth: true, role: 'student' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const role = localStorage.getItem('role')
  if (to.meta.requiresAuth && !token) return next('/login')
  if (to.meta.role && to.meta.role !== role) return next('/login')
  next()
})

export default router