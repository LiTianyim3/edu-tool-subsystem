import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login:          (data) => api.post('/api/v1/auth/login', data),
  register:       (data) => api.post('/api/v1/auth/register', data),
  getMe:          ()     => api.get('/api/v1/auth/me'),
  changePassword: (data) => api.put('/api/v1/auth/change-password', data),
  sendResetCode:  (data) => api.post('/api/v1/auth/send-reset-code', data),
  resetPassword:  (data) => api.post('/api/v1/auth/reset-password', data),
}

export default api