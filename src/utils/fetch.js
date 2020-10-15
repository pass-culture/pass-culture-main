import { API_URL } from './config'

const NO_CONTENT_STATUS = 204

export const fetchFromApiWithCredentials = (path, method, body) => {
  const bodyParams = body ? { body: JSON.stringify(body) } : {}
  const init = {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    method: method || 'GET',
    ...bodyParams,
  }

  return fetch(`${API_URL}${path}`, init).then(response => {
    if (!response.ok) throw Error('HTTP error')
    if (response.status !== NO_CONTENT_STATUS) {
      return response.json()
    }
  })
}
