import { db } from './dexie'
import { fetchData } from './fetch'

export async function syncData (method, path, config = {}) {
  const data = await db[path].toArray()
  return { data }
}

export async function putUserMediations (result) {
  if (result.data) {
    return db.userMediations.bulkPut(result.data)
  }
}

export async function syncUserMediations () {
  const result = await fetchData('POST', 'userMediations')
  putUserMediations(result)
}

export async function clearUserMediations () {
  db.userMediations.clear()
}
