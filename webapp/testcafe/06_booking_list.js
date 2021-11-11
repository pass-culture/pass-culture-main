import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

fixture('Mes réservations,')

test('en consultant la liste de mes réservations, pour chaque offre', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_06_booking_list',
    'get_existing_webapp_user_with_bookings'
  )
  const section = Selector('.mb-my-booking')
  const tokenLink = section.find('.mb-token-link')
  const linkToVerso = section.find('.teaser-link')
  const token = Selector('.qr-code-token')
  const backLink = Selector('.back-link')

  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}reservations`)

    // je peux accéder à l'offre en cliquant sur la tuile
    .click(linkToVerso)
    .click(backLink)

    // je peux accéder à la contremarque en cliquant sur "Voir le QR code"
    .click(tokenLink)
    .expect(token.exists)
    .ok()
    .click(backLink)
})
