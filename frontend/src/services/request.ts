import axios from 'axios'
import { message } from 'antd'

// 统一请求实例：baseURL 走 vite 代理到后端 /api
const request = axios.create({
  baseURL: '/api',
  timeout: 20000,
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail =
      error?.response?.data?.detail ||
      error?.message ||
      '请求失败，请检查后端服务是否已启动'
    message.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    return Promise.reject(error)
  },
)

export default request
