import Dexie from 'dexie'
import flatten from 'lodash.flatten'
import uniq from 'lodash.uniq'
import uuid from 'uuid'

import { fetchData } from './request'

export const config = {
  name: "pass_culture",
  collections: [
    {
      description: 'id',
      name: 'userMediations',
      query: ({ around }) => around && `around=${around}`
    },
    {
      description: 'id',
      name: 'differences'
    }
  ],
  version: 1
}

const storesConfig = {}
config.collections.forEach(({ description, name }) =>
  storesConfig[name] = description)

export const db = new Dexie(config.name)
db.version(config.version).stores(storesConfig)

export async function putData (dexieMethod, path, data) {
  const collectionName = path.split('?')[0]
  const table = db[collectionName]
  if (!table) {
    return
  }
  if (dexieMethod === 'bulk') {
    console.log('data', data)
    await table.clear()
    await table.bulkPut(data)
  } else if (dexieMethod === 'update') {
    await Promise.all(data.map(datum => table.update(datum.id, datum)))
    await db.differences.add({
      id: uuid(),
      name: collectionName,
      ids: data.map(datum => datum.id)
    })
  }
  return table.toArray()
}

export async function clear () {
  const tables = db.tables.filter(table => !table.differences)
  return Promise.all(tables.map(async table => table.clear()))
}

export async function fetch (config = {}) {
  const tables = db.tables.filter(table => !table.differences)
  const results = await Promise.all(tables.map(async table =>
    await table.toArray()))
  if (config.console) {
    console.log(results)
  }
  return results
}

export async function pushPull (state = {}) {
  return Promise.all(config.collections.map(async ({ name, query }) => {
    // remove differences
    if (name === 'differences') {
      return
    }
    // table
    const table = db[name]
    // push
    const differences = await db.differences.filter(difference =>
      difference.name === name).toArray()
    const entityIds = uniq(flatten(
      differences.map(difference => difference.ids)))
    await db.differences.clear()
    const entities = await table.filter(entity => entityIds.includes(entity.id))
                                .toArray()
    let config = {}
    if (entities) {
      config.body = entities
    }
    // fetch
    const method = 'PUT'
    let path = table.name
    if (query) {
      const pathQuery = typeof query === 'function' ? query(state) : query
      if (pathQuery && pathQuery !== '') {
        path = `${path}?${pathQuery}`
      }
    }
    const result = await fetchData(method, path, config)
    // bulk
    if (result.data) {
      return putData('bulk', path, result.data, { isClear: true })
    } else {
      console.warn(result.error)
    }
  }))
}
