import { Selector } from 'testcafe'

import {
  navigateAfterVenueSubmit,
  navigateToOffererAs,
} from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const addressInput = Selector('input[name="address"]')
const addressSuggestion = Selector('.location-viewer .menu .item')
const cityInput = Selector('input[name="city"]')
const descriptionInput = Selector('textarea[name="description"]')
const commentInput = Selector('textarea[name="comment"]')
const venueType = Selector('#venue-type')
const venueTypeOption = Selector('#venue-type option')
const latitudeInput = Selector('input[name="latitude"]')
const longitudeInput = Selector('input[name="longitude"]')
const nameInput = Selector('input[name="name"]')
const postalCodeInput = Selector('input[name="postalCode"]')
const siretInput = Selector('input[name="siret"]')
const audioDisabilityCompliant = Selector(
  'input[name="audioDisabilityCompliant"]'
)

fixture('En étant sur la page de création d’un lieu,')

test('je peux créer un lieu avec un SIRET valide', async t => {
  const { offerer, user } = await fetchSandbox(
    'pro_05_venue',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue'
  )
  const { siren } = offerer

  const newVenueButton = Selector(`a`).withText('Créer un lieu')
  const latitude = '48.863666'
  const longitude = '2.337933'
  const venueName = `MINISTERE DE LA CULTURE`
  const siret = `${siren}12345`
  const address = '3 RUE DE VALOIS'
  const city = 'Paris'
  const postalCode = '75001'

  const description =
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc id risus lorem. Curabitur elementum auctor interdum. In quis risus nibh. Ut gravida leo sit amet purus aliquam elementum. Aliquam erat volutpat. Sed mi ligula, porttitor at mi a, sollicitudin blandit diam. Quisque malesuada, ante lobortis luctus luctus, nisi elit porta diam, at imperdiet ex velit nec erat.'

  await navigateToOffererAs(user, offerer, createUserRole(user))(t)

  await t
    .click(newVenueButton)
    .click(venueType)
    .click(venueTypeOption.withText('Festival'))
    .typeText(siretInput, siret, { paste: true })
    .typeText(descriptionInput, description, { paste: true })
    .click(audioDisabilityCompliant)
    .expect(nameInput.value)
    .eql(venueName)
    .expect(addressInput.value)
    .eql(address)
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

test('je peux créer un lieu sans SIRET avec une description', async t => {
  const { offerer, user } = await fetchSandbox(
    'pro_05_venue',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue'
  )
  const newVenueButton = Selector(`a`).withText('Créer un lieu')
  const toggleSiretOrComment = Selector(`button`).withText(
    'Je veux créer un lieu avec SIRET'
  )

  await navigateToOffererAs(user, offerer, createUserRole(user))(t)

  await t
    .click(newVenueButton)
    .click(toggleSiretOrComment)
    .typeText(nameInput, 'Le lieu sympa de type sans siret', { paste: true })
    .typeText(commentInput, 'Test sans SIRET', { paste: true })
    .click(venueType)
    .click(venueTypeOption.withText('Festival'))
    .typeText(addressInput, '1 place du trocadéro Paris')
    .click(addressSuggestion)
    .click(audioDisabilityCompliant)
    .expect(postalCodeInput.value)
    .eql('75016')
    .expect(cityInput.value)
    .eql('Paris')
    .expect(latitudeInput.value)
    .eql('48.862412')
    .expect(longitudeInput.value)
    .eql('2.282002')
  await navigateAfterVenueSubmit('creation')(t)
})
