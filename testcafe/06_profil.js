import { youngUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

fixture`03_01 Page Profil`.beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}profil`)
})
