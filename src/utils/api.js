import 'fetch-everywhere'

import { API_URL } from './config'

export async function apiData (method, path, config = {}) {
  // unpack
  const { body, token } = config
  // init
  const init = { method,
    // mode: 'cors',
    // credentials: 'include'
  }
  if (method && method !== 'GET') {
    init.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }
  if (body) {
    init.body = JSON.stringify(body)
  }
  if (token) {
    if (!init.headers) {
      init.headers = {}
    }
    init.headers.Authorization = `Bearer ${token}`
  }
  // fetch
  const result = await fetch(`${API_URL}/${path}`, init)
  if (result.status === 200) {
    return { data: await result.json() }
  } else {
    return { error: await result.json() }
  }
}
