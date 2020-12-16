import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'

fixture('Sur le carrousel,')

test('je suis redirigé vers la home', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_03_decouverte',
    'get_existing_webapp_user_with_bookings'
  )

  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}decouverte`)
    .expect(getPageUrl())
    .contains('/accueil')
})
