import { createUserRole } from './helpers/roles'
import { hasSignedUpUser93 } from './helpers/users'
import { ROOT_PATH } from '../src/utils/config'

fixture`03_01 Page Profil`.beforeEach(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}profil`)
})
