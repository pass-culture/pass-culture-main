import 'fetch-everywhere'

import { URL } from './config'

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
  const result = await fetch(`${URL}/${path}`, init)
  return result.json && await result.json()
}
