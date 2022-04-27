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

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'method' implicitly has an 'any' type.
const buildOptions = (method, withCredentials = true) => {
  const options = {
    method: method,
  }
  if (method !== GET_HTTP_METHOD && method !== DELETE_HTTP_METHOD) {
    // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
    options['headers'] = { 'Content-Type': 'application/json' }
  }

  if (withCredentials) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'credentials' does not exist on type '{ m... Remove this comment to see the full error message
    options.credentials = 'include'
  }
  return options
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
const buildUrl = path => `${API_URL}${path}`

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
const fetchWithErrorHandler = async (path, options) => {
  try {
    const response = await fetch(buildUrl(path), options)
    const results = NOT_JSON_BODY_RESPONSE_STATUS.includes(response.status)
      ? null
      : await response.json()
    if (!response.ok) {
      if (response.status === HTTP_STATUS.SERVICE_UNAVAILABLE) {
        // @ts-expect-error ts-migrate(2322) FIXME: Type 'string | undefined' is not assignable to typ... Remove this comment to see the full error message
        window.location.href = URL_FOR_MAINTENANCE
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
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  getPlainText: async (path, withCredentials = true) => {
    const options = buildOptions(GET_HTTP_METHOD, withCredentials)
    // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
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
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  getExcelFile: async (path, withCredentials = true) => {
    const options = buildOptions(GET_HTTP_METHOD, withCredentials)
    // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
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
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  get: async (path, withCredentials = true) => {
    return await fetchWithErrorHandler(
      path,
      buildOptions(GET_HTTP_METHOD, withCredentials)
    )
  },
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  post: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('POST', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  postWithFormData: async (path, data, withCredentials = true) => {
    let options = buildOptions('POST', withCredentials)
    // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
    options['headers'] = { encode: 'multipart/form-data' }
    options = {
      ...options,
      // @ts-expect-error ts-migrate(2322) FIXME: Type '{ body: any; method: any; }' is not assignab... Remove this comment to see the full error message
      body: data,
    }
    return await fetchWithErrorHandler(path, options)
  },
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  put: async (path, data, withCredentials = true) => {
    const options = {
      ...buildOptions('PUT', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  patch: async (path, data = {}, withCredentials = true) => {
    const options = {
      ...buildOptions('PATCH', withCredentials),
      body: JSON.stringify(data),
    }
    return await fetchWithErrorHandler(path, options)
  },
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'path' implicitly has an 'any' type.
  delete: async (path, withCredentials = true) => {
    return await fetchWithErrorHandler(
      path,
      buildOptions(DELETE_HTTP_METHOD, withCredentials)
    )
  },
}
