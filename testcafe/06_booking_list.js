import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'

import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const section = Selector('.mb-my-booking')
const contremarque = section.find('.mb-token')
const datetimeSpan = section.find('.teaser-sub-title')
const linkToVerso = section.find('.teaser-link')

const versoContent = Selector('.verso-content')
const addressInfo = versoContent.find('address')

const dateTimeRegexMatcher = /^(?:Dimanche|Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi)\s(\d{1,2})([/-])(\d{1,2})\2(\d{4})\s([à])\s(\d{1,2})([:])(\d{1,2})/

let userRole

fixture('En consultant la liste de mes réservations, pour chaque "tuile"')

test('Je vois la contremarque', async t => {
  userRole = await createUserRoleFromUserSandbox(
    'webapp_06_booking_list',
    'get_existing_webapp_user_with_bookings'
  )
  await t.useRole(userRole).navigateTo(`${ROOT_PATH}reservations`)
  await t.expect(contremarque.exists).ok()
})

test("Je vois la date et l'heure", async t => {
  userRole = await createUserRoleFromUserSandbox(
    'webapp_06_booking_list',
    'get_existing_webapp_user_with_bookings'
  )
  await t.useRole(userRole).navigateTo(`${ROOT_PATH}reservations`)

  await t
    .expect(datetimeSpan.exists)
    .ok()
    .expect(datetimeSpan.innerText)
    .match(dateTimeRegexMatcher)
})

test('Je vois le lieu sur le verso', async t => {
  userRole = await createUserRoleFromUserSandbox(
    'webapp_06_booking_list',
    'get_existing_webapp_user_with_bookings'
  )
  await t.useRole(userRole).navigateTo(`${ROOT_PATH}reservations`)

  await t
    .expect(linkToVerso.exists)
    .ok()
    .click(linkToVerso)
    .wait(500)
    .expect(addressInfo.exists)
    .ok()
})
