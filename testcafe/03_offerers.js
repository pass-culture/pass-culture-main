import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const activationMessage = Selector('ul.actions li.is-italic')
const arrow = Selector('.caret a')
const backAnchor = Selector('a.button.is-secondary')
const closeButton = Selector('.close')
const createOfferAnchor = Selector('a.button.is-primary')
const createOffererAnchor = Selector(
  "a.button.is-primary[href='/structures/nouveau']"
)
const firstArrow = arrow.nth(0)
const modalContent = Selector('.modal-content')
const navbarLink = Selector('a.navbar-link, span.navbar-burger').filterVisible()
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const pageTitleHeader = Selector('h1')
const subTitleHeader = Selector('h2')

fixture`03_01 OfferersPage | Je me connecte pour la première fois en tant que nouvel utilisateur·ice`.beforeEach(
  async t => {
    await t.useRole(regularOfferer)
    // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
  }
)

test("J'arrive sur la page /offres après m'être connecté·e", async t => {
  await t.expect(pageTitleHeader.innerText).eql('Vos offres')
})

test("Je ne peut pas encore créer d'offre car je n'ai pas ajouté de lieu, une modale m'informe et je suis redirigé·e vers la page /structures", async t => {
  await t
    .expect(createOfferAnchor.innerText)
    .eql('\nCréer une offre\n')
    .click(createOfferAnchor)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
  await t
    .expect(modalContent.innerText)
    .eql(
      'Vous devez avoir déjà enregistré un lieu dans une de vos structures pour ajouter des offres\n'
    )
  await t.wait(2000).click(closeButton)

  const structuresLocation = await t.eval(() => window.location)
  await t.expect(structuresLocation.pathname).eql('/structures')
})

fixture`03_02 OfferersPage | Voir la liste de mes structures`.beforeEach(
  async t => {
    await t
      .useRole(regularOfferer)
      .click(navbarLink)
      .click(offerersNavbarLink)
  }
)

test("La structure qui vient d'être créée est en attente de validation", async t => {
  await t
    .expect(activationMessage.innerText)
    .eql('En cours de validation : vous allez recevoir un e-mail.')
})

test("Je peux voir les détails d'une structure (THEATRE NATIONAL DE CHAILLOT)", async t => {
  await t.click(firstArrow)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
  await t.expect(subTitleHeader.innerText).eql('THEATRE NATIONAL DE CHAILLOT')
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
