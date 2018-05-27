import Dexie from 'dexie'
import flatten from 'lodash.flatten'
import moment from 'moment'
import uniq from 'lodash.uniq'
import uuid from 'uuid'

import config from './config'
import { fetchData } from '../../utils/request'
import { IS_DEV, IS_DEXIE } from '../../utils/config'

const storesConfig = {}
const collections = config.collections
collections.forEach(({ description, name }) =>
  (storesConfig[name] = description))

export const db = IS_DEXIE
  ? new Dexie(config.name)
  : {}

if (IS_DEXIE) {
  db.version(config.version).stores(storesConfig)
  if (config.upgrate) {
    db.upgrade(config.upgrate)
  }
} else {
  db.tables = []
  config.collections.forEach(({ description, name }) => {
    db[name] = { data: [], name }
    db.tables.push(db[name])
  })
}

export async function getData(collectionName, query) {
  // check
  const table = db[collectionName]
  if (!table) {
    return
  }
  const { sortBy } = collections.find(collection =>
    collection.name === collectionName)
  // get
  let data = table
  if (query && Object.keys(query).length) {
    data = data.filter(element =>
      Object.keys(query).every(key => element[key] === query[key])
    )
  }
  // dexie
  if (IS_DEXIE) {
    if (sortBy) {
      data = await table.filter(() => true)
                        .sortBy(sortBy)
    } else {
      data = await data.toArray()
    }
  } else {
    data = table.data
  }
  // return
  return { data }
}

export async function putData(
  dexieMethod,
  collectionName,
  dataOrDatum,
  config = {}
) {
  // unpack
  const diff = (typeof config.diff !== 'undefined' && config.diff) || true
  // check the table
  let table = db[collectionName]
  if (!table) {
    return
  }
  const { description, sortBy } = collections.find(collection =>
    collection.name === collectionName)
  const result = { collectionName }
  // check format
  let data = Array.isArray(dataOrDatum)
    ? dataOrDatum
    : [dataOrDatum]
  // update is when we want to update certain elements in the array
  let storedData = IS_DEXIE
    ? await table.toArray()
    : table.data
  // look for deprecation
  result.deprecatedData = []
  for (let datum of data) {
    const storedDatum = storedData.find(({ id }) =>
      id === datum.id)
    if (storedDatum) {
      // bind temporaly the storedDatum
      datum._storedDatum = storedDatum
      if (
        storedDatum.dateCreated &&
        datum.dateCreated &&
        moment(storedDatum.dateCreated) < moment(datum.dateCreated)
      ) {
        result.deprecatedData.push(storedDatum)
      }
    }
  }
  // bulk
  if (dexieMethod === 'bulk') {
    // bulk is when we replace everything and index by the index in the array data
    await table.clear()
    if (data && data.length === 0) {
      result.data = []
      return result
    }
    const bulkData = data.map(datum => {
      if (datum._storedDatum) {
        delete datum._storedDatum
      }
      return datum
    })
    if (IS_DEXIE) {
      await table.bulkPut(bulkData)
        //.catch(error =>
        // console.log('BULK ERROR', error))
      result.data = table
      if (sortBy) {
        result.data = await result.data.filter(() => true)
                                        .sortBy(sortBy)
      } else {
        result.data = await result.data.toArray()
      }
    } else {
      table.data = bulkData
      result.data = table.data
    }
    return result
  }
  // update
  for (let datum of data) {
    if (datum._storedDatum) {
      let localStoredDatum = datum._storedDatum
      if (!localStoredDatum[description]) {
        // console.warn('storedDatum has not the description as a good key')
      }
      const putDatum = Object.assign({}, localStoredDatum, datum)
      delete datum._storedDatum
      if (putDatum[description]) {
        if (IS_DEXIE) {
          await table
            .put(putDatum[description], putDatum)
            //.catch(error => {})
        } else {
          localStoredDatum = Object.assign(localStoredDatum,  putDatum)
        }
      }
    } else {
      if (IS_DEXIE) {
        await table.add(datum)
           //.catch(error => {
          //   console.log('YA UNE ERROR', error.message, collectionName, datum)
          // })
      } else {
        table.data.push(datum)
      }
    }
  }
  // diff or not
  if (IS_DEXIE && diff) {
    await db.differences.add({
      id: uuid(),
      name: collectionName,
      ids: data.map(datum => datum.id),
    })
  }
  // get again
  result.data = IS_DEXIE
    ? await table.toArray()
    : table.data
  return result
}

export async function clear() {
  if (IS_DEXIE) {
    const tables = db.tables.filter(table => !table.differences)
    return Promise.all(tables.map(async table => table.clear()))
  } else {
    config.collections.forEach(({ name }) => db[name].data = [])
  }
}

export async function fetch(config = {}) {
  const tables = db.tables.filter(table => !table.differences)
  const results = IS_DEXIE
    ? await Promise.all(
      tables.map(async table => await table.toArray())
    )
    : tables.map(table => table.data)
  if (config.console) {
    console.log(results)
  }
  return results
}

export async function setUser(state = {}) {
  const { user } = state
  if (!user) {
    console.warn('We set user in dexie but user is not defined')
  }
  if (IS_DEXIE) {
    await db.users.clear()
    await db.users.add(user)
  } else {
    db.users.data = [user]
  }
}

export async function pushPull(state = {}) {
  return Promise.all(
    config.collections.map(async ({
      isPullOnly,
      isSync,
      name,
      query,
      orderBy
    }) => {
      // just do that for the collection with isSync or isPullOnly
      if (!isSync && !isPullOnly) {
        return
      }
      // table
      const table = db[name]
      // push
      if (IS_DEXIE && isSync) {
        const differences = await db.differences
          .filter(difference => difference.name === name)
          .toArray()
        const entityIds = uniq(
          flatten(differences.map(difference => difference.ids))
        )
        await db.differences
          .filter(difference => difference.name === name)
          .delete()
        const entities = await table
          .filter(entity => entityIds.includes(entity.id))
          .toArray()
        let config = {}
        if (entities) {
          config.body = entities
        }
      }
      // fetch
      const method = isPullOnly ? 'GET' : 'PUT'
      let path = table.name
      if (query) {
        const pathQuery = typeof query === 'function'
          ? query(state)
          : query
        if (pathQuery && pathQuery !== '') {
          path = `${path}?${pathQuery}`
        }
      }
      const result = await fetchData(method, path, config)
      // bulk
      if (result.data) {
        const pathWithoutQuery = path.split('?')[0]
        const collectionName = pathWithoutQuery.split('/')[0]
        if (IS_DEXIE) {
          return await putData('bulk', collectionName, result.data, {
              isClear: true,
              orderBy
            })
        } else {
          db[collectionName].data = result.data
        }
      } else {
        return result
      }
    })
  )
}

if (IS_DEV) {
  if (typeof window !== 'undefined') {
    window.clearDexie = clear
    window.dexieDb = db
    window.fetchDexie = fetch
    window.pushPullDexie = pushPull
  }
}
