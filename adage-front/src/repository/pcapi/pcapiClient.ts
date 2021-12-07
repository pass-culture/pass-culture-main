import { API_URL, URL_FOR_MAINTENANCE } from 'utils/config'
export const HTTP_STATUS = {
  NO_CONTENT: 204,
  FORBIDDEN: 403,
  SERVICE_UNAVAILABLE: 503,
}
const GET_HTTP_METHOD = 'GET'
const DELETE_HTTP_METHOD = 'DELETE'
const POST_HTTP_METHOD = 'POST'

const buildOptions = method => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')
  const headers: HeadersInit = new Headers()
  headers.set('Authorization', `Bearer ${token}`)

  if (method !== GET_HTTP_METHOD && method !== DELETE_HTTP_METHOD) {
    headers.set('Content-Type', 'application/json')
  }

  return {
    headers,
    method: method,
  }
}

const buildUrl = path => `${API_URL}${path}`

const fetchWithErrorHandler = async (path, options) => {
  const response = await fetch(buildUrl(path), options)
  const contentType = response.headers.get('content-type')
  const results =
    contentType && contentType.includes('application/json')
      ? await response.json()
      : await response.text()
  if (!response.ok) {
    if (response.status === HTTP_STATUS.SERVICE_UNAVAILABLE) {
      window.location.href = URL_FOR_MAINTENANCE
    }
    return Promise.reject(
      results ? { errors: results, status: response.status } : null
    )
  }
  return Promise.resolve(results)
}

export const client = {
  get: async (path: string): Promise<any> => {
    return await fetchWithErrorHandler(path, buildOptions(GET_HTTP_METHOD))
  },
  post: async (path: string, data: Record<string, unknown>): Promise<any> => {
    const options = {
      ...buildOptions(POST_HTTP_METHOD),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
}
