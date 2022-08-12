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

test('je peux modifier mon profil avec de nouvelles données valides.', async t => {
  const { user } = await fetchSandbox('pro_14_home_profile', 'get_pro_user')

  const modifyProfileButton = Selector(
    '[data-testid="card-profile"] button'
  ).withText('Modifier')
  const submitProfileButton = Selector('button').withText('Enregistrer')

  const inputFirstname = Selector('input[name="first-name-input"]')
  const inputLastname = Selector('input[name="last-name-input"]')
  const inputEmail = Selector('input[name="email-input"]')
  const inputPhoneNumber = Selector('input[name="phone-input"]')

  const editData = {
    firstname: 'new firstname',
    lastname: 'new lastname',
    email: 'edited@email.com',
    phoneNumber: '01 99 99 99 99',
  }
  const editedUserFirstname = Selector('span').withText(editData.firstname)
  const editedUserLastname = Selector('span').withText(editData.lastname)
  const editedUserEmail = Selector('span').withText(editData.email)
  const editedUserPhoneNumber = Selector('span').withText(editData.phoneNumber)
  const notificationSuccess = Selector('.notification.is-success').withText(
    'Les informations ont bien été enregistrées.'
  )
  const errorMessages = Selector('.it-errors')

  await navigateToHomeAs(user, createUserRole(user))(t)
  await t
    .click(modifyProfileButton)

    .expect(inputFirstname.exists)
    .eql(true)
    .expect(inputLastname.exists)
    .eql(true)
    .expect(inputEmail.exists)
    .eql(true)
    .expect(inputPhoneNumber.exists)
    .eql(true)

    .expect(errorMessages.count)
    .eql(0)

    .selectText(inputFirstname)
    .typeText(inputFirstname, editData.firstname, { paste: true })
    .selectText(inputLastname)
    .typeText(inputLastname, editData.lastname, { paste: true })
    .selectText(inputEmail)
    .typeText(inputEmail, editData.email, { paste: true })
    .selectText(inputPhoneNumber)
    .typeText(inputPhoneNumber, editData.phoneNumber, { paste: true })
    .click(submitProfileButton)

    .expect(errorMessages.count)
    .eql(0)

    .expect(inputFirstname.exists)
    .eql(false)
    .expect(inputLastname.exists)
    .eql(false)
    .expect(inputEmail.exists)
    .eql(false)
    .expect(inputPhoneNumber.exists)
    .eql(false)

    .expect(notificationSuccess.exists)
    .eql(true)

    .expect(editedUserFirstname.exists)
    .eql(true)
    .expect(editedUserLastname.exists)
    .eql(true)
    .expect(editedUserEmail.exists)
    .eql(true)
    .expect(editedUserPhoneNumber.exists)
    .eql(true)
})
