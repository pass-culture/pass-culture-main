import { Selector } from 'testcafe'

import { validatedOffererUserRole } from './helpers/roles'

const activationMessage = Selector('#offerer-item-validation')
const arrow = Selector('.caret a')
const backAnchor = Selector('a.button.is-secondary')
const createOffererAnchor = Selector(
  "a.button.is-primary[href='/structures/nouveau']"
)
const firstArrow = arrow.nth(0)
const navbarLink = Selector('a.navbar-link, span.navbar-burger').filterVisible()
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const pageTitleHeader = Selector('h1')
const subTitleHeader = Selector('h2')

fixture`03_01 OfferersPage | Je me connecte pour la première fois en tant que nouvel utilisateur·ice`.beforeEach(
  async t => {
    await t.useRole(validatedOffererUserRole)
    // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
  }
)

test("J'arrive sur la page /offres après m'être connecté·e", async t => {
  await t.expect(pageTitleHeader.innerText).eql('Vos offres')
})

fixture`03_02 OfferersPage | Voir la liste de mes structures`.beforeEach(
  async t => {
    await t
      .useRole(validatedOffererUserRole)
      .click(navbarLink)
      .click(offerersNavbarLink)
  }
)

test("La structure qui vient d'être créée est en attente de validation", async t => {
  await t
    .expect(activationMessage.innerText)
    .eql("Structure en cours de validation par l'équipe Pass Culture.")
})

test("Je peux voir les détails d'une structure", async t => {
  await t.click(firstArrow)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
  await t.expect(subTitleHeader.exists).ok()
})

test('Je peux rattacher une nouvelle structure', async t => {
  await t.click(createOffererAnchor)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures/nouveau')
  await t
    .expect(pageTitleHeader.innerText)
    .eql('Structure')

    .click(backAnchor)
  const newLocation = await t.eval(() => window.location)
  await t.expect(newLocation.pathname).eql('/structures')
})
