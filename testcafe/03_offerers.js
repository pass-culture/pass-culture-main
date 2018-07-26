import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const pageTitle = Selector('h1')
const createOfferButton = Selector('a.button.is-primary')
const modalContent = Selector('.modal-content')
const closeButton = Selector('.close')
const navbarLink = Selector('a.navbar-link')
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")

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

    fixture `03_01 OffererSPage | Voir la liste de mes structures`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
    })

    test("La structure qui vient d'être créée est en attente de validation", async t => {

      // navigation
      await t
        .click(navbarLink)
        .click(offerersNavbarLink)

        // En cours de validation : vous allez recevoir un e-mail.

    })
