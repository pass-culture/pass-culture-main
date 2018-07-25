import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const pageTitle = Selector('h1')
const createOfferButton = Selector('a.button.is-primary')
const modalDialog = Selector('.modal-dialog')
const modalContent = Selector('.modal-content')
const closeButton = Selector('.close')

fixture `03_01 OfferersPage | Je me connecte pour la première fois en tant que nouvel utilisateur·ice`
    .beforeEach( async t => {
      await t
      .useRole(regularOfferer)
      // le userRole a l'option preserveUrl: true donc le test commence sur la page /offres
    })

    test("J'arrive sur la page /offres après m'être connecté·e", async t => {
      await t.expect(pageTitle.innerText).eql('Vos offres')
      //TODO En attente de la possibilité de créer un nouvel utilisateur pour ce test. Tout de suite après la création, l'user arrive sur /structures
    })

    test("Je ne peut pas encore créer d'offre car je n'ai pas ajouté de lieu, une modale m'informe et je suis redirigé·e vers la page /structures", async t => {
      // TODO Ne fonctionne que quand la base de données est vide
      await t.expect(createOfferButton.innerText).eql('\nCréer une offre\n')
      .click(createOfferButton)
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/offres/nouveau')
      await t.expect(modalContent.innerText).eql('Vous devez avoir déjà enregistré un lieu dans une de vos structures pour ajouter des offres\n')
      .click(closeButton)
      await t.expect(modalDialog.visible).ok()
      .wait(2000)

      const structuresLocation = await t.eval(() => window.location)
      await t.expect(structuresLocation.pathname).eql('/structures')
    })
