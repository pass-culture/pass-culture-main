import { API_URL } from './config'

export const fetchFromApiWithCredentials = path => {
  const pathWithBeginningSlash = path.startsWith('/') ? path : `/${path}`
  return fetch(`${API_URL}${pathWithBeginningSlash}`, { credentials: 'include' }).then(response => {
    if (!response.ok) throw Error('HTTP error')
    return response.json()
  })
}
