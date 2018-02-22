import Dexie from 'dexie'

import { fetchData } from './fetch'

export const db = new Dexie("pass_culture")
db.version(1).stores({
  userMediations: 'id'
})

export async function putUserMediations (result) {
  if (result.data) {
    return db.userMediations.bulkPut(result.data)
  }
}

export async function syncUserMediations () {
  const result = await fetchData('POST', 'userMediations')
  putUserMediations(result)
}
