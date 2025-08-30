import axios from 'axios'

// Use process.env for Create React App (not import.meta.env which is for Vite)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analyzeFeature = async (featureData) => {
  const response = await api.post('/api/analyze', featureData)
  return response.data
}

export const bulkAnalyze = async (features) => {
  const response = await api.post('/api/bulk-csv-analysis-json', { items: features })
  return response.data
}

export const getSystemHealth = async () => {
  const response = await api.get('/api/health')
  return response.data
}

export const getRagStatus = async () => {
  const response = await api.get('/api/rag_status')
  return response.data
}

export const toggleRag = async (enable = null) => {
  const params = enable !== null ? { enable } : {}
  const response = await api.post('/api/toggle_rag', null, { params })
  return response.data
}

export const refreshCorpus = async () => {
  const response = await api.post('/api/refresh_corpus')
  return response.data
}

export const downloadEvidence = async (featureId = null) => {
  const params = featureId ? { feature_id: featureId } : {}
  const response = await api.get('/api/evidence', {
    params,
    responseType: 'blob'
  })
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'evidence.zip')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export default api