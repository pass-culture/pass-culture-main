import { Selector } from 'testcafe'

import {
  navigateToOffererAs,
  navigateAfterVenueSubmit,
} from './helpers/navigations'
import { fetchSandbox } from './helpers/sandboxes'
import { getSiretRequestMockAs } from './helpers/sirenes'

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
  const { address, city, name, postalCode, siren } = offerer

  const newVenueButton = Selector(`a`).withText('Créer un lieu')
  const latitude = '48.862923'
  const longitude = '2.287896'
  const venueName = `${name} - Lieu`
  const siret = `${siren}12345`
  const venue = {
    address,
    city,
    latitude,
    longitude,
    name: venueName,
    postalCode,
    siret,
  }

  const description =
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc id risus lorem. Curabitur elementum auctor interdum. In quis risus nibh. Ut gravida leo sit amet purus aliquam elementum. Aliquam erat volutpat. Sed mi ligula, porttitor at mi a, sollicitudin blandit diam. Quisque malesuada, ante lobortis luctus luctus, nisi elit porta diam, at imperdiet ex velit nec erat.'

  await navigateToOffererAs(user, offerer)(t)

  await t
    .addRequestHooks(getSiretRequestMockAs(venue))
    .click(newVenueButton)
    .click(venueType)
    .click(venueTypeOption.withText('Festival'))
    .typeText(siretInput, siret)
    .typeText(descriptionInput, description)
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

  await navigateToOffererAs(user, offerer)(t)

  await t
    .click(newVenueButton)
    .typeText(nameInput, 'Le lieu sympa de type sans siret')
    .typeText(commentInput, 'Test sans SIRET')
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
