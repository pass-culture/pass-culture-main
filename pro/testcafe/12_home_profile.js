import { Selector } from 'testcafe'

import { getPathname } from './helpers/location'
import { HOME_URL, navigateToHomeAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

fixture("En étant sur la page d'accueil,")

test('j’ai accès aux informations de mon profil', async t => {
  const { user } = await fetchSandbox('pro_14_home_profile', 'get_pro_user')

  const cardProfile = Selector('[data-testid="card-profile"]')
  const userFirstname = Selector('span').withText(user.firstName)
  const userLastname = Selector('span').withText(user.lastName)
  const userEmail = Selector('span').withText(user.email)
  const userPhoneNumber = Selector('span').withText('+33 1 00 00 00 09')

  await navigateToHomeAs(user, createUserRole(user))(t)
  await t
    .expect(getPathname())
    .eql(HOME_URL)
    .expect(cardProfile.exists)
    .eql(true)
    .expect(userFirstname.exists)
    .eql(true)
    .expect(userLastname.exists)
    .eql(true)
    .expect(userEmail.exists)
    .eql(true)
    .expect(userPhoneNumber.exists)
    .eql(true)
})
