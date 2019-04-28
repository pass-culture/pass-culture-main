import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateAfterVenueSubmit,
  navigateToNewVenueAs,
  navigateToVenueAs,
} from './helpers/navigations'
import { getSiretRequestMockAs } from './helpers/sirenes'

const form = Selector('form#venue')
const mapMarker = Selector('.leaflet-marker-pane img')
const adressInput = Selector('input[name="address"]')
const backAnchor = Selector('a.back-button')
const cityInput = Selector('input[name="city"]')
const closeAnchor = Selector('button.close').withText('OK')

const bookingEmailInput = Selector('input[name="bookingEmail"]')
const latitudeInput = Selector('input[name="latitude"]')
const longitudeInput = Selector('input[name="longitude"]')
const nameInput = Selector('input[name="name"]')
const postalCodeInput = Selector('input[name="postalCode"]')
const notificationError = Selector('.notification.is-danger')
const notificationSuccess = Selector('.notification.is-success.columns')
const siretInput = Selector('input[name="siret"]')
const commentInput = Selector('textarea[name="comment"]')
const siretInputError = Selector('input[name="siret"]').find('.field-errors')
const submitButton = Selector('button.button.is-primary') //créer un lieu
const updateAnchor = Selector('a.button.is-secondary') //modifier un lieu
const venueMarker = Selector('img.leaflet-marker-icon')

fixture('Venue A | Créer un nouveau lieu avec succès').beforeEach(async t => {
  t.ctx.sandbox = await fetchSandbox(
    'pro_05_venue',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue'
  )
  const { offerer, user } = t.ctx.sandbox
  return navigateToNewVenueAs(user, offerer)(t)
})

test('Je rentre une nouveau lieu via son siret avec succès', async t => {
  // given
  const { offerer } = t.ctx.sandbox
  const { address, city, name, postalCode, siren } = offerer
  const latitude = '48.862923'
  const longitude = '2.287896'
  const venueName = `${name} - Lieu`
  const siret = `${siren}12345`
  const future_venue_with_offerer_siret = {
    address,
    city,
    latitude,
    longitude,
    name: venueName,
    postalCode,
    siret,
  }
  await t.addRequestHooks(
    getSiretRequestMockAs(future_venue_with_offerer_siret)
  )

  // when
  await t.typeText(siretInput, siret)

  // then
  await t.expect(nameInput.value).eql(venueName)
  await t.expect(adressInput.value).eql(address)
  await t.expect(postalCodeInput.value).eql(postalCode)
  await t.expect(cityInput.value).eql(city)
  await t.expect(latitudeInput.value).eql(latitude)
  await t.expect(longitudeInput.value).eql(longitude)
  const marker = `${latitude}-${longitude}`
  await t.expect(venueMarker.getAttribute('alt')).eql(marker)
  await navigateAfterVenueSubmit('creation')(t)
})

test('Je rentre un nouveau lieu sans siret avec succès', async t => {
  // given
  const addressInput = Selector('#venue-address')
  const addressSuggestion = Selector('.geo-input .menu .item')
  const address = '1 place du trocadéro'
  const banAddress = '1 Place du Trocadero et du 11 Novembre 75016 Paris'
  const city = 'Paris'
  const comment = 'Test sans SIRET'
  const latitude = '48.862923'
  const longitude = '2.287896'
  const name = 'Le lieu sympa de type sans siret'
  const postalCode = '75016'

  // when
  await t
    .typeText(nameInput, name)
    .typeText(commentInput, comment)
    .typeText(addressInput, address)

  // then
  await t.expect(addressSuggestion.innerText).eql(banAddress)

  // when
  await t.click(addressSuggestion)

  // then
  await t
    .expect(postalCodeInput.value)
    .eql(postalCode)
    .expect(cityInput.value)
    .eql(city)
    .expect(latitudeInput.value)
    .eql(latitude)
    .expect(longitudeInput.value)
    .eql(longitude)

  await navigateAfterVenueSubmit('creation')(t)
})

fixture("Venue B | Je ne peux pas créer de lieu, j'ai des erreurs").beforeEach(
  async t => {
    t.ctx.sandbox = await fetchSandbox(
      'pro_05_venue',
      'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_at_least_one_physical_venue'
    )
    const { offerer, user } = t.ctx.sandbox
    return navigateToNewVenueAs(user, offerer)(t)
  }
)

test('Une entrée avec cet identifiant existe déjà', async t => {
  // when
  const { venue } = t.ctx.sandbox
  const { siret } = venue
  await t.addRequestHooks(getSiretRequestMockAs(venue))
  await t.typeText(siretInput, siret)
  await t.click(submitButton)

  // then
  await t
    .expect(siretInputError.innerText)
    .contains(
      'Une entrée avec cet identifiant existe déjà dans notre base de données'
    )
    .expect(notificationError.innerText)
    .contains('Formulaire non validé\nOK')

  // when
  await t
    .click(closeAnchor)
    // please be careful, this wait prevents is necessary
    // to pass every time, otherwise succes of this test is
    // kind of random!
    .wait(10000)

  // then
  await t.expect(notificationError.exists).notOk()
})

test('Il est obligatoire de saisir le commentaire', async t => {
  // then
  await t
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit être requis par défaut')

  // when
  await t.typeText(siretInput, '123')
  // then
  await t
    .expect(commentInput.hasAttribute('required'))
    .notOk("Comment n'est pas requis si le SIRET est saisi")

  // when
  await t.selectText(siretInput).pressKey('delete')
  // then
  await t
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit être requis à nouveau si SIRET est effacé')

  // when
  await t.typeText(commentInput, 'lorem ipsum dolor sit amet')
  // then
  await t
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit rester requis même saisi')
    .expect(siretInput.hasAttribute('required'))
    .notOk("SIRET n'est pas requis")
})

test('Le code SIRET doit correspondre à un établissement de votre structure', async t => {
  // given
  await t.typeText(siretInput, '492475033 00022')

  // when
  await t.click(submitButton)

  // then
  await t
    .expect(siretInputError.innerText)
    .contains(
      'Le code SIRET doit correspondre à un établissement de votre structure'
    )
    .expect(notificationError.innerText)
    .contains('Formulaire non validé\nOK')
})

test('La saisie de mauvaise coordonées géographique ne crash pas la page', async t => {
  // when
  await t.typeText(latitudeInput, '45')
  // then
  await t.expect(form.exists).ok()

  // when
  await t.selectText(latitudeInput).typeText(latitudeInput, '45.3')
  // then
  await t.expect(form.exists).ok()

  // when
  await t.selectText(latitudeInput).typeText(latitudeInput, '45,3')
  // then
  await t.expect(form.exists).ok()

  // when
  await t
    .selectText(latitudeInput)
    .pressKey('delete')
    .typeText(latitudeInput, 'ABC')
  // then
  await t
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)

  // when
  await t.pressKey('delete').typeText(latitudeInput, '---')
  // then
  await t.expect(form.exists).ok()

  // when
  await t
    .selectText(latitudeInput)
    .pressKey('delete')
    .typeText(latitudeInput, ' ')
  // then
  await t.expect(form.exists).ok()
})

test('La saisie de bonnes coordonées géographiques ajoute un marker', async t => {
  // given
  await t.expect(mapMarker.exists).notOk()

  // when
  await t.typeText(latitudeInput, '45').typeText(longitudeInput, '3.5')

  // then
  await t
    .expect(form.exists)
    .ok()
    .expect(mapMarker.exists)
    .ok()
})

fixture('Venue C | Je suis sur la page de détail du lieu').beforeEach(
  async t => {
    t.ctx.sandbox = await fetchSandbox(
      'pro_05_venue',
      'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_at_least_one_physical_venue'
    )
    const { offerer, user, venue } = t.ctx.sandbox
    return navigateToVenueAs(user, offerer, venue)(t)
  }
)

test('Je peux revenir en arrière', async t => {
  // when
  await t.click(backAnchor)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
})

test.only("Je peux modifier l'email de contact du lieu", async t => {
  // given
  await t.wait(5000)
  const originalEmail = bookingEmailInput.value

  // when
  await t
    .click(updateAnchor)
    .typeText(bookingEmailInput, 'rosa.soulot@example.net', { replace: true })
    .click(submitButton)

  // then
  await t
    .expect(bookingEmailInput.value)
    .notEql(originalEmail)
    .expect(bookingEmailInput.value)
    .eql('rosa.soulot@example.net')
    .expect(notificationSuccess.innerText)
    .contains('Lieu modifié avec succès !')
})
