import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const activationMessage = Selector('ul.actions li.is-italic')
const arrow = Selector('.caret a')
const backButton = Selector('a.button.is-secondary')
const closeButton = Selector('.close')
const createOfferButton = Selector('a.button.is-primary')
const createOffererButton = Selector("a.button.is-primary[href='/structures/nouveau']")
const firstArrow = arrow.nth(0)
const modalContent = Selector('.modal-content')
const navbarLink = Selector('a.navbar-link')
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const pageTitle = Selector('h1')
const subTitle = Selector('h2')

fixture `03_01 OfferersPage | Je me connecte pour la première fois en tant que nouvel utilisateur·ice`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
      // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
    })

    test("J'arrive sur la page /offres après m'être connecté·e", async t => {
      await t.expect(pageTitle.innerText).eql('Vos offres')
    })

    test("Je ne peut pas encore créer d'offre car je n'ai pas ajouté de lieu, une modale m'informe et je suis redirigé·e vers la page /structures", async t => {
      await t
        .expect(createOfferButton.innerText).eql('\nCréer une offre\n')
        .click(createOfferButton)
      const location = await t.eval(() => window.location)
      await t
        .expect(location.pathname).eql('/offres/nouveau')
      await t.expect(modalContent.innerText)
             .eql('Vous devez avoir déjà enregistré un lieu dans une de vos structures pour ajouter des offres\n')
     await t
      .wait(2000)
      .click(closeButton)

      const structuresLocation = await t.eval(() => window.location)
      await t.expect(structuresLocation.pathname).eql('/structures')
    })

    fixture `03_02 OffererSPage | Voir la liste de mes structures`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
      .click(navbarLink)
      .click(offerersNavbarLink)
    })

    test("La structure qui vient d'être créée est en attente de validation", async t => {
      await t.expect(activationMessage.innerText).eql('En cours de validation : vous allez recevoir un e-mail.')
    })

    test("Je peux voir les détails d'une structure (THEATRE NATIONAL DE CHAILLOT)", async t => {
      await t
        .click(firstArrow)
        const location = await t.eval(() => window.location)
        await t.expect(location.pathname).eql('/structures/AE')
        await t.expect(subTitle.innerText).eql('THEATRE NATIONAL DE CHAILLOT')
    })

    test("Je peux rattacher une nouvelle structure", async t => {
      await t
        .click(createOffererButton)
        const location = await t.eval(() => window.location)
        await t.expect(location.pathname).eql('/structures/nouveau')
        await t.expect(pageTitle.innerText).eql('Structure')

        .click(backButton)
        const newLocation = await t.eval(() => window.location)
        await t.expect(newLocation.pathname).eql('/structures')
    })
