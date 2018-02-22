import { db, putUserMediations } from './dexie'
import { requestData } from '../reducers/data'

export async function syncData (method, path, config = {}) {
  const data = await db[path].toArray()
  return { data }
}

export async function clearUserMediations () {
  db.userMediations.clear()
}

export function requestUserMediationsData () {
  return requestData('POST', 'userMediations', { hook: putUserMediations })
}
