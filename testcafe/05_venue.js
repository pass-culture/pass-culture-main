import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateAfterVenueSubmit } from './helpers/navigations'
import { getSiretRequestMockAs } from './helpers/sirenes'
import { createUserRole } from './helpers/roles'

const addressInput = Selector('input[name="address"]')
const addressSuggestion = Selector('.location-viewer .menu .item')
const cityInput = Selector('input[name="city"]')
const commentInput = Selector('textarea[name="comment"]')
const latitudeInput = Selector('input[name="latitude"]')
const longitudeInput = Selector('input[name="longitude"]')
const nameInput = Selector('input[name="name"]')
const postalCodeInput = Selector('input[name="postalCode"]')
const siretInput = Selector('input[name="siret"]')
const newVenueButton = Selector('a').withText('+ Ajouter un lieu')

fixture("En étant sur la page de création d'un lieu")

test('Je peux créer un lieu avec un SIRET valide', async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_05_venue',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue'
  )
  const { address, city, id: offererId, name, postalCode, siren } = offerer
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
  await t
    .addRequestHooks(getSiretRequestMockAs(venue))
    .useRole(createUserRole(user))
    .navigateTo('/structures/' + offererId)
    .click(newVenueButton)

  // when
  await t.typeText(siretInput, siret)

  // then
  await t
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

test('Je peux créer un lieu sans SIRET', async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_05_venue',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue'
  )
  const { id: offererId } = offerer
  const address = '1 place du trocadéro Paris'
  const city = 'Paris'
  const comment = 'Test sans SIRET'
  const latitude = '48.862412'
  const longitude = '2.282002'
  const name = 'Le lieu sympa de type sans siret'
  const postalCode = '75016'
  await t
    .useRole(createUserRole(user))
    .navigateTo('/structures/' + offererId)
    .click(newVenueButton)

  // when
  await t
    .typeText(nameInput, name)
    .typeText(commentInput, comment)
    .typeText(addressInput, address)

  // then
  await t
    .click(addressSuggestion)
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
