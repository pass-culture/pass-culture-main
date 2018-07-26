import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'

import { regularOfferer } from './helpers/roles'

const backButton = Selector("a.back-button.has-text-primary.active")
const cancelButton = Selector('a.back-button')
const createOfferButton = Selector("a.button.is-primary[href='/offres/nouveau?lieu=AE']")


fixture `06_01 OfferPage | Créer une nouvelle offre`

test("Lorsque je clique sur le bouton créer une offre sur la page d'un lieu, j'accède au formulaire de création d'offre", async t => {
  await t
    .useRole(regularOfferer)
    .navigateTo(ROOT_PATH+'structures/AE/lieux/AE')

  await t
    .click(createOfferButton)
    .wait(500)
    const location = await t.eval(() => window.location)
    // await t.expect(location.pathname).eql('/offres/nouveau?lieu=AE')
    await t.expect(location.pathname).eql('/offres/nouveau')

  // await t
    // .click(cancelButton)
    // await t.expect(location.pathname).eql('/offres')
})

// annuler renvoie vers /offres
