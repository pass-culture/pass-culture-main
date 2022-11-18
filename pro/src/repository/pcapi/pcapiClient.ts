/* istanbul ignore file */

import { API_URL, URL_FOR_MAINTENANCE } from 'utils/config'
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
        // @ts-expect-error ts-migrate(2322) FIXME: Type 'string | undefined' is not assignable to typ... Remove this comment to see the full error message
        window.location.assign(URL_FOR_MAINTENANCE)
      }
      return Promise.reject(
        results ? { errors: results, status: response.status } : null
      )
    }
    return Promise.resolve(results)
  } catch (err) {
    return Promise.reject(null)
  }
}

export const client = {
  getPlainText: async (path: string, withCredentials = true) => {
    const options = buildOptions(GET_HTTP_METHOD, withCredentials)
    options['headers'] = { 'Content-Type': 'text/plain' }

    try {
      const response = await fetch(buildUrl(path), options)
      if (response.status !== 200) {
        throw Error('An error happened.')
      }
      return Promise.resolve(await response.text())
    } catch (e) {
      return Promise.reject(e)
    }
  },
  getExcelFile: async (path: string, withCredentials = true) => {
    const options = buildOptions(GET_HTTP_METHOD, withCredentials)
    options['headers'] = { 'Content-Type': 'application/vnd.ms-excel' }

    try {
      const response = await fetch(buildUrl(path), options)
      if (response.status !== 200) {
        throw Error('An error happened.')
      }
      return Promise.resolve(await response.arrayBuffer())
    } catch (e) {
      return Promise.reject(e)
    }
  },
  get: async (path: string, withCredentials = true) => {
    return await fetchWithErrorHandler(
      path,
      buildOptions(GET_HTTP_METHOD, withCredentials)
    )
  },
  post: async (
    path: string,
    data: Record<string, any>,
    withCredentials = true
  ) => {
    const options = {
      ...buildOptions('POST', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
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
  put: async (
    path: string,
    data: Record<string, any>,
    withCredentials = true
  ) => {
    const options = {
      ...buildOptions('PUT', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  patch: async (path: string, data = {}, withCredentials = true) => {
    const options = {
      ...buildOptions('PATCH', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  delete: async (path: string, withCredentials = true) => {
    return await fetchWithErrorHandler(
      path,
      buildOptions(DELETE_HTTP_METHOD, withCredentials)
    )
  },
}
