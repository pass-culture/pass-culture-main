import { API_URL } from './config'

const NO_CONTENT_STATUS = 204

export const fetchFromApiWithCredentials = (path, method, body) => {
  const bodyParams = body ? { body: JSON.stringify(body) } : {}

  method = method || 'GET'

  const init = {
    credentials: 'include',
    method: method,
    ...bodyParams,
  }

  if (method !== 'GET') {
    init['headers'] = {
      'Content-Type': 'application/json',
    }
  }

  return fetch(`${API_URL}${path}`, init).then(response => {
    if (!response.ok) throw response
    if (response.status !== NO_CONTENT_STATUS) {
      return response.json()
    }
  })
}
