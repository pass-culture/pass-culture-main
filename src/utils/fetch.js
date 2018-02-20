import 'fetch-everywhere'

import { API_URL } from './config'

export async function fetchData (method, path, config = {}) {
  // unpack
  const { body, position, token } = config
  // init
  const init = { method,
    // mode: 'cors',
    credentials: 'include'
  }
  if (method && method !== 'GET') {
    init.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    // body
    init.body = JSON.stringify(body || {})
  }
  // position
  if (position) {
    const { latitude, longitude } = position.coords
    if (body) {
      init.body.latitude = latitude
      init.body.longitude = longitude
    } else {
      const positionQuery = `latitude=${latitude}&&longitude=${longitude}`
      path = `${path}${path.includes('?') ? '&&' : '?'}${positionQuery}`
    }
  }
  // token
  if (token) {
    if (!init.headers) {
      init.headers = {}
    }
    init.headers.Authorization = `Bearer ${token}`
  }
  // fetch
  const result = await fetch(`${API_URL}/${path}`, init)
  if (result.status === 200 || result.status === 201) {
    return { data: await result.json() }
  } else {
    return { error: await result.json() }
  }
}
