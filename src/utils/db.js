import Dexie from 'dexie'

const db = new Dexie("pass_culture")
db.version(1).stores({
    mediations: 'dateRead'
})

export default db
