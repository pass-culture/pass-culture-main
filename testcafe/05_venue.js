import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const navbarLink = Selector('a.navbar-link')
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const offererButton  = Selector("a[href^='/structures/']").withText('THEATRE NATIONAL DE CHAILLOT')
const newVenueButton  = Selector("a.button.is-secondary").withText("+ Ajouter un lieu")

const siretInput = Selector('#venue-siret')
const nameInput = Selector("#venue-name")
const adressInput = Selector("#venue-address")
const postalCodeInput = Selector("#venue-postalCode")
const cityInput = Selector("#venue-city")
const latitudeInput = Selector("#venue-latitude")
const longitudeInput = Selector("#venue-longitude")
const submitButton  = Selector('button.button.is-primary') //connexion

fixture `05_ VenuePage | Créer un nouveau lieu`
  .beforeEach( async t => {
    await t
    .useRole(regularOfferer)
    // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
  })

test("Je rentre une nouveau lieu via son siret", async t => {

  // TODO Ne fonctionne pas
  // navigation
  await t
    .click(navbarLink)
    .click(offerersNavbarLink)
    .click(offererButton)
    .wait(500)
    .click(newVenueButton)

  // input
  await t
    .typeText(siretInput, '69203951400017')
    .wait(1000)

  // check other completed fields
  await t.expect(nameInput.value).eql("THEATRE NATIONAL DE CHAILLOT")
  await t.expect(adressInput.value).eql("1 PL TROCADERO ET DU 11 NOVEMBRE")
  await t.expect(postalCodeInput.value).eql("75116")
  await t.expect(cityInput.value).eql("PARIS 16")
  await t.expect(latitudeInput.value).eql("48.862923")
  await t.expect(longitudeInput.value).eql("2.287896")

})
