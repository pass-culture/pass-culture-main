import { API_URL } from 'utils/config'

const buildOptions = (method, withCredentials = true) => {
  const options = {
    headers: { 'Content-Type': 'application/json' },
    method: method,
  }
  if (withCredentials) {
    options.credentials = 'include'
  }
  return options
}

const buildUrl = path => `${API_URL}${path}`

const fetchWithErrorHandler = async (path, options) => {
  const response = await fetch(buildUrl(path), options)
  if (!response.ok) {
    throw Error('HTTP error')
  }
  const results = response.statusText !== 'NO CONTENT' ? await response.json() : null
  return Promise.resolve(results)
}

export const client = {
  get: async (path, withCredentials = true) => {
    return await fetchWithErrorHandler(path, buildOptions('GET', withCredentials))
  },
  post: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('POST', withCredentials),
      body: JSON.stringify(data),
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
  patch: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('PATCH', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
}
