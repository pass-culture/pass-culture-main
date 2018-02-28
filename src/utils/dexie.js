import Dexie from 'dexie'
import moment from 'moment'

import { fetchData } from './request'

export const config = {
  name: "pass_culture",
  collections: [
    {
      description: 'id',
      name: 'userMediations',
      query: ({ around }) => around && `around=${around}`
    }
  ],
  version: 1
}

const storesConfig = {}
config.collections.forEach(({ description, name }) =>
  storesConfig[name] = description)

export const db = new Dexie(config.name)
db.version(config.version).stores(storesConfig)

export async function bulkData (method, path, data) {
  let dbMethod = method.toLowerCase()
  dbMethod = `bulk${dbMethod[0].toUpperCase()}${dbMethod.slice(1)}`
  const collectionName = path.split('?')[0]
  const table = db[collectionName]
  if (!table) {
    return
  }
  await table.clear()
  return table[dbMethod](data)
}

export async function clear () {
  return Promise.all(db.tables.map(async table => table.clear()))
}

export async function fetch (config = {}) {
  const results = await Promise.all(db.tables.map(async table =>
    await table.toArray()))
  if (config.console) {
    console.log(results)
  }
  return results
}

export async function pull (store = {}) {
  return Promise.all(config.collections.map(async ({ name, query }) => {
    const table = db[name]
    const method = 'PUT'
    let path = table.name
    if (query) {
      const pathQuery = typeof query === 'function' ? query(store) : query
      if (pathQuery && pathQuery !== '') {
        path = `${path}?${pathQuery}`
      }
    }
    const result = await fetchData(method, path)
    if (result.data) {
      return bulkData(method, path, result.data)
    } else {
      console.warn(result.error)
    }
  }))
}
