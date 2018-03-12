import 'fetch-everywhere'

import { API_URL } from './config'
import { db, putData } from './dexie'

export const isRequestAction = ({ type }) => /REQUEST_(.*)/.test(type)

export const isSuccessAction = ({ type }) => /SUCCESS_(.*)/.test(type)

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
  const collectionName = path.split('?')[0]
  if (result.status === 200 || result.status === 201) {
    return { data: await result.json() }
  } else {
    return { errors: await result.json() }
  }
}

export async function syncData (method, path, config = {}) {
  // unpack
  const { body } = config
  let data
  if (method === 'GET') {
    data = await db[path].toArray()
  } else {
    data = await putData('update', path, body)
  }
  return { data }
}
