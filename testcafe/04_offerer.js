import { Selector } from 'testcafe'

import {
  navigateToNewOffererAs,
  navigateToOffererAs,
} from './helpers/navigations'
import {
  FUTURE_OFFERER_CREATED_IN_OFFERER_PAGE_WITH_NO_IBAN,
  OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN,
} from './helpers/offerers'
import {
  SIREN_ALREADY_IN_DATABASE,
  SIREN_WITHOUT_ADDRESS,
} from './helpers/sirens'
import { VALIDATED_UNREGISTERED_OFFERER_USER } from './helpers/users'

const addressInput = Selector('input#offerer-address')
const nameInput = Selector('input#offerer-name')
const sirenInput = Selector('#offerer-siren')
const sirenErrorInput = Selector('#offerer-siren-error')
const submitButton = Selector('button.button.is-primary') //connexion

fixture`OffererPage A | Créer une nouvelle structure`.beforeEach(
  navigateToNewOffererAs(VALIDATED_UNREGISTERED_OFFERER_USER)
)

test('Je peux naviguer vers une nouvelle structure et revenir aux structures', async t => {
  const backAnchor = Selector('a.button.is-secondary')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures/nouveau')

  await t.click(backAnchor)
  const newLocation = await t.eval(() => window.location)
  await t.expect(newLocation.pathname).eql('/structures')
})

test('Je ne peux pas ajouter de nouvelle structure avec un siren faux', async t => {
  // navigation
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')

    // input
    .typeText(sirenInput, '69256356275794356243264')

  // submit
  await t.click(submitButton)

  // api return an error message
  await t.expect(sirenErrorInput.innerText).contains('Siren invalide')
})

test.requestHooks(SIREN_ALREADY_IN_DATABASE)(
  'Je ne peux pas ajouter de nouvelle structure ayant un siren déjà existant dans la base',
  async t => {
    // navigation
    let location = await t.eval(() => window.location)
    await t
      .expect(location.pathname)
      .eql('/structures/nouveau')

      // input
      .typeText(sirenInput, OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN.siren)

    // submit
    await t.click(submitButton)

    // api return an error message
    await t
      .expect(sirenErrorInput.innerText)
      .contains(
        'Une entrée avec cet identifiant existe déjà dans notre base de données'
      )
  }
)

test('Je rentre une nouvelle structure via son siren', async t => {
  const {
    address,
    name,
    siren,
  } = FUTURE_OFFERER_CREATED_IN_OFFERER_PAGE_WITH_NO_IBAN

  // navigation
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')

    // input
    .typeText(sirenInput, siren)

  // check other completed fields
  await t.expect(nameInput.value).eql(name)
  await t.expect(addressInput.value).eql(address)

  // submit
  await t.click(submitButton)

  // check location success change
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test.requestHooks(SIREN_WITHOUT_ADDRESS)(
  "Je rentre une structure dont l'adresse n'est pas renvoyée par l'api sirene et je peux valider",
  async t => {
    // given
    const sirenWithNoAddress = '216 701 375'

    let location = await t.eval(() => window.location)
    await t
      .typeText(sirenInput, sirenWithNoAddress)
      .expect(addressInput.value)
      .eql('')

      // when
      .click(submitButton)

    // then
    location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures')
  }
)

fixture`OffererPage B | Modifier une structure`

test.skip('Je modifie une structure pour lui ajouter ses coordonnées bancaires car je suis admin', async t => {
  // given
  await navigateToOffererAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN
  )(t)

  // when
  // t.typeText(bicInput, 'BNPAFRPP')
  // t.typeText(ibanInput, 'FR7630004000031234567890143')

  // then
  // TODO
})
