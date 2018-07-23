import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const navbarLink = Selector('a.navbar-link')
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const offererButton  = Selector("a").withText('THEATRE NATIONAL DE CHAILLOT')
const newVenueButton  = Selector("a.button.is-secondary").withText("+ Ajouter un lieu")

const siretInput = Selector('#input_venues_siret')
const nameInput = Selector("#input_venues_name")
const adressInput = Selector("#input_venues_address")
const postalCodeInput = Selector("#input_venues_postalCode")
const cityInput = Selector("#input_venues_city")
const latitudeInput = Selector("#input_venues_latitude")
const longitudeInput = Selector("#input_venues_longitude")
const submitButton  = Selector('button.button.is-primary') //connexion

fixture `05_ VenuePage | Créer un nouveau lieu`
  .beforeEach( async t => {
    await t
    .useRole(regularOfferer)
    // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
  })

test("Je rentre une nouveau lieu via son siret", async t => {

  // navigation
  await t
    .click(navbarLink)
    .click(offerersNavbarLink)
    .click(offererButton)
    .click(newVenueButton)

  // input
  await t
    .typeText(siretInput, '69203951400017')
    .wait(1000)

  // check other completed fields
  await t.expect(nameInput.value).eql("THEATRE NATIONAL DE CHAILLOT")
  await t.expect(adressInput.value).eql("1 Place du Trocadero et du 11 Novembre 75016 Paris")
  await t.expect(postalCodeInput.value).eql("75116")
  await t.expect(cityInput.value).eql("PARIS 16")
  await t.expect(latitudeInput.value).eql("48.862923")
  await t.expect(longitudeInput.value).eql("2.287896")

  // submit
  await t
    .click(submitButton)
    .wait(1000)

    // check location success change
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures')
})
