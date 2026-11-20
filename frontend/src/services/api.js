import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '')
const API = axios.create({ baseURL: API_BASE })

function triggerDownload(url) {
  const link = document.createElement('a')
  link.href = url
  link.target = '_blank'
  link.rel = 'noopener noreferrer'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const newsletterApi = {
  generate: (payload = {}) => {
    const data = typeof payload === 'string' ? { template: payload } : payload
    return API.post('/newsletter/generate', data)
  },
  list: () => API.get('/newsletter/list'),
  get: (id) => API.get(`/newsletter/${id}`),
  preview: (id) => API.get(`/newsletter/${id}/preview`),
  download: (id) => triggerDownload(`${API_BASE}/newsletter/${id}/download`),
  downloadWord: (id) => triggerDownload(`${API_BASE}/newsletter/${id}/download-word`),
  regenerateTool: (id, toolNum) => API.post(`/newsletter/${id}/regenerate-tool/${toolNum}`),
  approve: (id) => API.put(`/newsletter/${id}/approve`),
  updateTool: (id, toolNum, data) => API.put(`/newsletter/${id}/tool/${toolNum}`, data),
  status: (id) => API.get(id && id !== 'undefined' ? `/newsletter/${id}/status` : '/newsletter/status'),
}

export const settingsApi = {
  get: () => API.get('/settings'),
  update: (data) => API.put('/settings', data),
}

export const historyApi = {
  tools: () => API.get('/history/tools'),
}
