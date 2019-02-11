import { Selector } from 'testcafe'

import {
  navigateAfterSubmit,
  navigateToNewVenueAs,
  navigateToVenueAs,
} from './helpers/navigations'
import {
  EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN,
  EXISTING_93_OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN,
} from './helpers/offerers'
import {
  EXISTING_PHYSICAL_VENUE_WITH_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN,
  FUTURE_PHYSICAL_VENUE_WITH_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN,
  FUTURE_PHYSICAL_VENUE_WITH_NO_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN,
} from './helpers/venues'
import { FUTURE_SIRET, SIRET_ALREADY_IN_DATABASE } from './helpers/sirens'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

const form = Selector('form#venue')
const mapMarker = Selector('.leaflet-marker-pane img')
const adressInput = Selector('#venue-address')
const backAnchor = Selector('a.back-button')
const cityInput = Selector('#venue-city')
const closeAnchor = Selector('button.close').withText('OK')

const emailInput = Selector('#venue-bookingEmail')
const latitudeInput = Selector('#venue-latitude')
const longitudeInput = Selector('#venue-longitude')
const nameInput = Selector('#venue-name')
const postalCodeInput = Selector('#venue-postalCode')
const notificationError = Selector('.notification.is-danger')
const notificationSuccess = Selector('.notification.is-success.columns')
const siretInput = Selector('#venue-siret')
const commentInput = Selector('#venue-comment')
const siretInputError = Selector('#venue-siret-error')
const submitButton = Selector('button.button.is-primary') //créer un lieu
const updateAnchor = Selector('a.button.is-secondary') //modifier un lieu
const venueMarker = Selector('img.leaflet-marker-icon')

fixture`VenuePage A | Créer un nouveau lieu avec succès`.beforeEach(
  navigateToNewVenueAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN
  )
)

test.requestHooks(FUTURE_SIRET)(
  'Je rentre une nouveau lieu via son siret avec succès',
  async t => {
    const {
      address,
      city,
      latitude,
      longitude,
      marker,
      name,
      postalCode,
      siret,
    } = FUTURE_PHYSICAL_VENUE_WITH_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN

    // when
    await t.typeText(siretInput, siret)

    // then
    await t.expect(nameInput.value).eql(name)
    await t.expect(adressInput.value).eql(address)
    await t.expect(postalCodeInput.value).eql(postalCode)
    await t.expect(cityInput.value).eql(city)
    await t.expect(latitudeInput.value).eql(latitude)
    await t.expect(longitudeInput.value).eql(longitude)
    await t.expect(venueMarker.getAttribute('alt')).eql(marker)

    await navigateAfterSubmit(t)
  }
)

test('Je rentre une nouveau lieu sans siret avec succès', async t => {
  // given
  const addressInput = Selector('#venue-address')
  const addressSuggestion = Selector('.geo-input .menu .item')
  const {
    address,
    banAddress,
    city,
    comment,
    latitude,
    longitude,
    name,
    postalCode,
  } = FUTURE_PHYSICAL_VENUE_WITH_NO_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN

  // when
  await t
    .typeText(nameInput, name)
    .typeText(commentInput, comment)
    .typeText(addressInput, address)

  // then
  await t
    .expect(addressSuggestion.innerText)
    .eql(banAddress)

    .click(addressSuggestion)

    .expect(postalCodeInput.value)
    .eql(postalCode)
    .expect(cityInput.value)
    .eql(city)
    .expect(latitudeInput.value)
    .eql(latitude)
    .expect(longitudeInput.value)
    .eql(longitude)

  await navigateAfterSubmit(t)
})

fixture`VenuePage B | Je ne peux pas créer de lieu, j'ai des erreurs`.beforeEach(
  navigateToNewVenueAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_93_OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN
  )
)

test.requestHooks(SIRET_ALREADY_IN_DATABASE)(
  'Une entrée avec cet identifiant existe déjà',
  async t => {
    // when
    const {
      siret,
    } = EXISTING_PHYSICAL_VENUE_WITH_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN
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

    // close notification div
    await t
      .click(closeAnchor)
      .wait(2000)
      .expect(notificationError.exists)
      .notOk()
  }
)

test('Il est obligatoire de saisir Le code SIRET OU le commentaire', async t => {
  await t
    .expect(siretInput.hasAttribute('required'))
    .ok('SIRET doit être requis par défaut')
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit être requis par défaut')

    .typeText(siretInput, '123')
    .expect(siretInput.hasAttribute('required'))
    .ok('SIRET doit rester requis même saisi')
    .expect(commentInput.hasAttribute('required'))
    .notOk('Comment ne devrait plus être requis quand SIRET est saisie')

    .selectText(siretInput)
    .pressKey('delete')
    .expect(siretInput.hasAttribute('required'))
    .ok('SIRET doit être requis par défaut')
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit être requis à nouveau si SIRET est effacé')

    .typeText(commentInput, 'lorem ipsum dolor sit amet')
    .expect(commentInput.hasAttribute('required'))
    .ok('Comment doit rester requis même saisi')
    .expect(siretInput.hasAttribute('required'))
    .notOk('SIRET ne devrait plus être requis quand Comment est saisie')
})

test('Le code SIRET doit correspondre à un établissement de votre structure', async t => {
  // input
  await t.typeText(siretInput, '492475033 00022')

  // create venue
  await t.click(submitButton)

  // error response
  await t
    .expect(siretInputError.innerText)
    .contains(
      'Le code SIRET doit correspondre à un établissement de votre structure'
    )
    .expect(notificationError.innerText)
    .contains('Formulaire non validé\nOK')
})

test('La saisie de mauvaise coordonées géographique ne crash pas la page', async t => {
  await t
    .typeText(latitudeInput, '45')
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)
    .typeText(latitudeInput, '45.3')
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)
    .typeText(latitudeInput, '45,3')
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)
    .pressKey('delete')
    .typeText(latitudeInput, 'ABC')
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)
    .pressKey('delete')
    .typeText(latitudeInput, '---')
    .expect(form.exists)
    .ok()
    .selectText(latitudeInput)
    .pressKey('delete')
    .typeText(latitudeInput, ' ')
    .expect(form.exists)
    .ok()
})

test('La saisie de bonnes coordonées géographiques ajoute un marker', async t => {
  await t
    // Given
    .expect(mapMarker.exists)
    .notOk()
    // when
    .typeText(latitudeInput, '45')
    .typeText(longitudeInput, '3.5')
    // then
    .expect(form.exists)
    .ok()
    .expect(mapMarker.exists)
    .ok()
})

fixture`VenuePage C | Je suis sur la page de détail du lieu`.beforeEach(
  navigateToVenueAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_93_OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN,
    EXISTING_PHYSICAL_VENUE_WITH_SIRET_WITH_93_OFFERER_IBAN_WITH_NO_IBAN
  )
)

test('Je peux revenir en arrière', async t => {
  // Navigate to offerer Detail page and found venue added
  await t.click(backAnchor)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
})

test("Je peux modifier l'email de contact du lieu", async t => {
  // Given
  await t.expect(emailInput.value).eql('fake@email.com')
  // When
  await t
    .click(updateAnchor)
    .typeText(emailInput, 'fake')
    .click(submitButton)
    .wait(500)
    // Then
    .expect(emailInput.value)
    .eql('fake@email.comfake')
    .expect(notificationSuccess.innerText)
    .contains('Lieu modifié avec succès !')
})
