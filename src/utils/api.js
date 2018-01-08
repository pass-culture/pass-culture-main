import 'fetch-everywhere'

import { URL } from './config'

export async function apiData (path, config = {}) {
  // unpack
  const { body, token } = config
  const method = config.method || 'GET'
  // init
  const init = { method }
  if (method && method !== 'GET') {
    init.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  }
  if (body) {
    init.body = body
  }
  if (token) {
    if (!init.headers) {
      init.headers = {}
    }
    init.headers.Authorization = `Bearer ${token}`
  }
  // fetch
  const result = await fetch(`${URL}/${path}`, init)
  const json = await result.json()
  return json
}
