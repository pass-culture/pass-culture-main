/* istanbul ignore file */

import { API_URL, URL_FOR_MAINTENANCE } from '@/commons/utils/config'
export const HTTP_STATUS = {
  NO_CONTENT: 204,
  FORBIDDEN: 403,
  SERVICE_UNAVAILABLE: 503,
}
const NOT_JSON_BODY_RESPONSE_STATUS = [
  HTTP_STATUS.NO_CONTENT,
  HTTP_STATUS.SERVICE_UNAVAILABLE,
]
const GET_HTTP_METHOD = 'GET'
const DELETE_HTTP_METHOD = 'DELETE'

const buildOptions = (method: string, withCredentials = true): RequestInit => {
  const options: RequestInit = {
    method: method,
  }
  if (method !== GET_HTTP_METHOD && method !== DELETE_HTTP_METHOD) {
    options['headers'] = { 'Content-Type': 'application/json' }
  }

  if (withCredentials) {
    options.credentials = 'include'
  }
  return options
}

const buildUrl = (path: string) => `${API_URL}${path}`

const fetchWithErrorHandler = async (path: string, options: RequestInit) => {
  try {
    const response = await fetch(buildUrl(path), options)
    const results = NOT_JSON_BODY_RESPONSE_STATUS.includes(response.status)
      ? null
      : await response.json()
    if (!response.ok) {
      if (response.status === HTTP_STATUS.SERVICE_UNAVAILABLE) {
        window.location.assign(URL_FOR_MAINTENANCE)
      }
      return Promise.reject(
        results ? { errors: results, status: response.status } : null
      )
    }
    return Promise.resolve(results)
  } catch {
    return Promise.reject(null)
  }
}

export const client = {
  postWithFormData: async (
    path: string,
    data: FormData,
    withCredentials = true
  ) => {
    let options = buildOptions('POST', withCredentials)
    options['headers'] = { encode: 'multipart/form-data' }
    options = {
      ...options,
      body: data,
    }
    return await fetchWithErrorHandler(path, options)
  },
}
