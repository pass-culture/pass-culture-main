import { ClientFunction } from 'testcafe'

import regularUser from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

fixture('O5_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 5000 })
})

fixture.skip('O5_02 Recherche | Après connexion').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test('Je peux accéder à la page /recherche', async t => {
  await t
  await t.expect(getPageUrl()).contains('/recherche', { timeout: 5000 })
})

// Je clique sur le menu vs navigateTo()

// RECHERCHE TEXTUELLE
// Je peux faire une recherche textuelle
// Je vois le filtre par type sous le formulaire de recherche textuelle
// Si j'ai des résultats : la page de résultats s'affiche, je ne vois pas le filtre par type sous le formulaire de recherche textuelle
// Si je n'ai pas de résultats, je vois le filtre par type sous le formulaire de recherche textuelle

// FILTRE
// Je fais apparaître et disparaître le menu de filtres
// Je peux faire une recherche détaillée
// par date
// DATE : Soit plusieurs laps de temps OU par une date précise (date picker)
// Je peux selectionner un des 4 distances proposées
// par type, je peux selectionner plusieurs types

// pour tout rénitialiser, il faut cliquer sur la croix dans le form et sur réninitaliser aussi donc

// Tu peux cumuler recherche textuelle + filtrage des résultats, et tu peux appliquer un filtre à toute la base d’offres puis faire une recherche textuelle dans la base filtrée
