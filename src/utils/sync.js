import { db } from './dexie'
import { fetchData } from './fetch'

export async function syncData (method, path, config = {}) {
  const data = await db[path].toArray()
  return { data }
}

export async function syncUserMediations () {
  const { data } = await fetchData('POST', 'userMediations')
  db.userMediations.bulkPut(data)
}

export async function clearUserMediations () {
  db.userMediations.clear()
}
