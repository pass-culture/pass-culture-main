import { API_URL } from 'utils/config'

export const HTTP_STATUS = {
  NO_CONTENT: 204,
  FORBIDDEN: 403,
}
const GET_HTTP_METHOD = 'GET'
const DELETE_HTTP_METHOD = 'DELETE'

const buildOptions = (method, withCredentials = true) => {
  const options = {
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

const buildUrl = path => `${API_URL}${path}`

const fetchWithErrorHandler = async (path, options) => {
  const response = await fetch(buildUrl(path), options)
  const results = response.status !== HTTP_STATUS.NO_CONTENT ? await response.json() : null
  if (!response.ok) {
    return Promise.reject(results ? { errors: results, status: response.status } : null)
  }
  return Promise.resolve(results)
}

export const client = {
  get: async (path, withCredentials = true) => {
    return await fetchWithErrorHandler(path, buildOptions(GET_HTTP_METHOD, withCredentials))
  },
  post: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('POST', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  postWithFormData: async (path, data, withCredentials = true) => {
    let options = buildOptions('POST', withCredentials)
    options['headers'] = { encode: 'multipart/form-data' }
    options = {
      ...options,
      body: data,
    }
    return await fetchWithErrorHandler(path, options)
  },
  put: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('PUT', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  patch: async (path, data = {}, withCredentials = true) => {
    const options = {
      ...buildOptions('PATCH', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  delete: async (path, withCredentials = true) => {
    return await fetchWithErrorHandler(path, buildOptions(DELETE_HTTP_METHOD, withCredentials))
  },
}
