const API_BASE = process.env.VUE_APP_API_BASE || 'http://127.0.0.1:8000/api/v1'
const API_ORIGIN = API_BASE.replace(/\/api\/v1$/, '')

async function parseResponse(response) {
  let data = null
  try {
    data = await response.json()
  } catch (error) {
    throw new Error('后端返回了无法解析的数据')
  }

  if (!response.ok || !data || data.code !== 0) {
    throw new Error((data && data.message) || '请求失败')
  }

  return data.data || {}
}

export async function postJSON(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body || {})
  })

  return parseResponse(response)
}

export async function postFile(path, file, fieldName = 'file') {
  const formData = new FormData()
  formData.append(fieldName, file)

  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData
  })

  return parseResponse(response)
}

export function buildOperator(currentUser) {
  return {
    username: currentUser && currentUser.username ? currentUser.username : 'tester01',
    role: currentUser && currentUser.role ? currentUser.role : 'tester'
  }
}

export function resolveAssetUrl(path) {
  if (!path) return ''
  if (/^(https?:)?\/\//.test(path) || path.startsWith('data:')) {
    return path
  }
  return `${API_ORIGIN}${path}`
}
