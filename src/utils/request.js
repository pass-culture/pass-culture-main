import 'fetch-everywhere'
import { parse } from 'query-string'

import { API_URL } from './config'
import { getData, putData } from '../workers/dexie/data'

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
  // const collectionName = path.split('?')[0]
  if (result.status === 200 || result.status === 201) {
    if (window.cordova) {
      window.cordova.plugins.CookieManagementPlugin.flush();
    }
    return { data: await result.json() }
  } else {
    return { errors: await result.json() }
  }
}

export async function localData (method, path, config = {}) {
  // unpack
  const { body } = config
  let data
  // check the table
  const [pathWithoutQuery, queryString] = path.split('?')
  const collectionName = pathWithoutQuery.split('/')[0]
  // call the good protocol api
  if (method === 'GET') {
    data = await getData(collectionName, parse(queryString))
  } else {
    data = await putData('update', collectionName, body)
    console.log('C ES', data)
  }
  // return data
  return { data }
}
