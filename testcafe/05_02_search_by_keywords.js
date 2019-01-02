import { Selector } from 'testcafe'

import { youngUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')

const resultsTitle = Selector('#results-title')

fixture
  .skip("O5_02_01 Recherche | J'effectue une recherche par mot-clé")
  .beforeEach(async t => {
    await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche/`)
  })

// ------------------------ RECHERCHE PAR MOTS-CLES

// ------------------------ NO RESULTS
// Je vois le filtre par type sous le formulaire de recherche textuelle

test.skip("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  await t
    .typeText(searchInput, 'fake')
    .click(keywordsSearchButton)
    .wait(500)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche/resultats')
  await t.expect(resultsTitle.innerText).eql('"FAKE" : 0 RÉSULTAT')
})

// TODO
// Si je n'ai pas de résultats, je vois la navigation par type sous le formulaire de recherche textuelle

// ------------------------ WITH RESULTS
test.skip("Je fais une recherche par mots-clés et j'ai des résultats", async t => {
  await t
    .typeText(searchInput, 'vhils')
    .click(keywordsSearchButton)
    .wait(500)
  await t.expect(resultsTitle.innerText).eql('"VHILS" : 1 RÉSULTAT')
})

// Si je clique sur l'offre d'une des vignettes, je suis redirigée vers la page découverte de cette offre...

// Quand on clique sur le bouton chercher, si le filtre est ouvert, il se referme mais la recherche reste active

// FILTRER et REINITIALISER S'affichent dans tous les cas (vu avec @IonLzr )
// Actuellement, quand je fais une recherche par mots-clés, puis que je clique sur le bouton flèche qui revient à la page de recherche, le champ contient toujours le mots-clés > doit il être vide ?
