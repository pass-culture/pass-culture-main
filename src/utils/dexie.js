import Dexie from 'dexie'

// Dexie.delete("pass_culture")
export const db = new Dexie("pass_culture")
db.version(1).stores({
    userMediations: 'id'
})
