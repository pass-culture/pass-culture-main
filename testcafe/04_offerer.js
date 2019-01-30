import { Selector } from 'testcafe'

import {
  navigateToNewOffererAs,
  navigateToOffererAs,
} from './helpers/navigations'
import {
  FUTURE_93_OFFERER_CREATED_IN_93_OFFERER_PAGE_WITH_NO_IBAN,
  EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN,
} from './helpers/offerers'
import {
  SIREN_ALREADY_IN_DATABASE,
  SIREN_WITHOUT_ADDRESS,
} from './helpers/sirens'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

const addressInput = Selector('input#offerer-address')
const nameInput = Selector('input#offerer-name')
const sirenInput = Selector('#offerer-siren')
const sirenErrorInput = Selector('#offerer-siren-error')
const submitButton = Selector('button.button.is-primary')

fixture`OffererPage A | Créer une nouvelle structure`.beforeEach(
  // given
  navigateToNewOffererAs(EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER)
)

test('Je peux naviguer vers une nouvelle structure et revenir aux structures', async t => {
  // given
  const backAnchor = Selector('a.button.is-secondary')
  const location = await t.eval(() => window.location)

  // then
  await t.expect(location.pathname).eql('/structures/nouveau')

  // when
  await t.click(backAnchor)

  // then
  const newLocation = await t.eval(() => window.location)
  await t.expect(newLocation.pathname).eql('/structures')
})

test('Je ne peux pas ajouter de nouvelle structure avec un siren faux', async t => {
  // given
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')
    .typeText(sirenInput, '69256356275794356243264')

  // when
  await t.click(submitButton)

  // then
  await t.expect(sirenErrorInput.innerText).contains('Siren invalide')
})

test.requestHooks(SIREN_ALREADY_IN_DATABASE)(
  'Je ne peux pas ajouter de nouvelle structure ayant un siren déjà existant dans la base',
  async t => {
    // given
    const { siren } = EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN
    let location = await t.eval(() => window.location)
    await t
      .expect(location.pathname)
      .eql('/structures/nouveau')
      .typeText(sirenInput, siren)

    // when
    await t.click(submitButton)

    // when
    await t
      .expect(sirenErrorInput.innerText)
      .contains(
        'Une entrée avec cet identifiant existe déjà dans notre base de données'
      )
  }
)

test('Je rentre une nouvelle structure via son siren', async t => {
  // given
  const {
    address,
    name,
    siren,
  } = FUTURE_93_OFFERER_CREATED_IN_93_OFFERER_PAGE_WITH_NO_IBAN
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')
    .typeText(sirenInput, siren)
  await t.expect(nameInput.value).eql(name)
  await t.expect(addressInput.value).eql(address)

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test.requestHooks(SIREN_WITHOUT_ADDRESS)(
  "Je rentre une structure dont l'adresse n'est pas renvoyée par l'api sirene et je peux valider",
  async t => {
    // given
    const sirenWithNoAddress = '216 701 375'
    let location = await t.eval(() => window.location)

    // when
    await t
      .typeText(sirenInput, sirenWithNoAddress)
      .expect(addressInput.value)
      .eql('')
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
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN
  )(t)

  // when
  // t.typeText(bicInput, 'BNPAFRPP')
  // t.typeText(ibanInput, 'FR7630004000031234567890143')

  // then
  // TODO
})
