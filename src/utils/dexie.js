import Dexie from 'dexie'

import { fetchData } from './request'

export const db = new Dexie("pass_culture")
db.version(1).stores({
  userMediations: 'id'
})
const config = { userMediations: 'unread' }

export async function bulkData (method, path, data) {
  let dbMethod = method.toLowerCase()
  dbMethod = `bulk${dbMethod[0].toUpperCase()}${dbMethod.slice(1)}`
  const collectionName = path.split('?')[0]
  const table = db[collectionName]
  return table && table[dbMethod](data)
}

export async function clear () {
  return Promise.all(db.tables.map(async table => table.clear()))
}

export async function fetch () {
  const results = await Promise.all(db.tables.map(async table =>
    await table.toArray()))
  return results
}

export async function pull () {
  return Promise.all(db.tables.map(async table => {
    const method = 'PUT'
    let path = table.name
    const query = config[table.name]
    if (query) {
      path = `${path}?${query}`
    }
    const result = await fetchData(method, path)
    if (result.data) {
      return bulkData(method, path, result.data)
    }
  }))
}
