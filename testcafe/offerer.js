import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const navbarLink = Selector('a.navbar-link')
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const newOffererButton  = Selector("a.button.is-primary[href='/structures/nouveau']")

const sirenInput = Selector('#input_offerers_siren')
const nameInput = Selector("#input_offerers_name")
const adressInput = Selector("#input_offerers_address")
const submitButton  = Selector('button.button.is-primary') //connexion

fixture `OffererPage | Créer une nouvelle structure`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
      // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
    })

test("Je rentre une nouvelle structure via son siren", async t => {

  // navigation
  await t
    .click(navbarLink)
    .click(offerersNavbarLink)
    .click(newOffererButton)

  // input
    .typeText(sirenInput, '692 039 514')
    .wait(1000)

  // check other completed fields
  await t.expect(nameInput.value).eql("THEATRE NATIONAL DE CHAILLOT")
  await t.expect(adressInput.value).eql("1 Place du Trocadero et du 11 Novembre 75016 Paris")

  // submit
  await t.click(submitButton)
         .wait(1000)

  // check location success change
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})
