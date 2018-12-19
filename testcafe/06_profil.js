import { youngUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

// Selecteurs

fixture`03_01 Page Profil`.beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}profil/`)
})

// tests

// TODO
// on a un header
// on a un footer avec un menu cliquable
// etc.
