import { Selector, RequestLogger } from 'testcafe'
import { API_URL } from '../src/utils/config'

import { regularOfferer } from './helpers/roles'

const LOGGER_URL = API_URL + '/offerers'

const logger = RequestLogger(LOGGER_URL, {
  logResponseBody: true,
  stringifyResponseBody: true,
  logRequestBody: true,
  stringifyRequestBody: true
})

const adressInput = Selector("input#offerer-address")
const nameInput = Selector("input#offerer-name")
const navbarLink = Selector('a.navbar-link')
const newOffererButton  = Selector("a.button.is-primary[href='/structures/nouveau']")
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const sirenInput = Selector('#offerer-siren')
const sirenErrorInput = Selector('p#offerer-siren-error span')
const submitButton  = Selector('button.button.is-primary') //connexion

fixture `04_01 OffererPage | Créer une nouvelle structure`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
      // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
      .click(navbarLink)
      .click(offerersNavbarLink)
      .click(newOffererButton)
    })

test.skip("Je ne peux pas ajouter de nouvelle structure avec un siren faux", async t => {

  // navigation
    let location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures/nouveau')

  // input
    .typeText(sirenInput, '69256356275794356243264')
    .wait(1000)

  // submit
    await t.click(submitButton)
    .wait(1000)

  // api return an error message
  await t.expect(sirenErrorInput.innerText).eql("Ce code SIREN est invalide")
})

test.skip
.requestHooks(logger)
("Je ne peux pas ajouter de nouvelle structure ayant un siren déjà existant dans la base", async t => {

  // navigation
    let location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures/nouveau')

  // input
    .typeText(sirenInput, '692 039 514')
    .wait(1000)

  // submit
    await t.click(submitButton)
    .wait(2000)

    console.log('logger.requests', logger.requests);

  // api return an error message
  await t.expect(sirenErrorInput.innerText).eql("\nUne entrée avec cet identifiant existe déjà dans notre base de données\n")
})

test.skip("Je rentre une nouvelle structure via son siren", async t => {

  // navigation
    let location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures/nouveau')

  // input
    .typeText(sirenInput, '492 475 033')
    .wait(1000)

  // check other completed fields
  await t.expect(nameInput.value).eql('NASKA PROD')
  await t.expect(adressInput.value).eql('167 QUAI DE VALMY')

  // submit
  await t.click(submitButton)
         .wait(1000)

  // check location success change
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})
