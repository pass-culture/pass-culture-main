import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

fixture('03_01 Page Profil').beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_06_profile',
    'get_existing_webapp_user_with_profile'
  )
  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}profil`)
})
