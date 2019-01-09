import { ClientFunction, Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { youngUserRole } from './helpers/roles'

const getPageUrl = ClientFunction(() => window.location.href.toString())

fixture('O5_01_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 500 })
})

fixture(
  "O5_03_01 Recherche | Je suis connecté·e | J'arrive sur la page de recherche | Home"
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche`)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)
const searchFilterMenu = Selector('#search-filter-menu')

test("Le filtre de recherche existe et l'icône n'est pas activé", async t => {
  await t
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
})

test("Je peux ouvrir et fermer le filtre en cliquand sur l'icône", async t => {
  const classFilterDiv = searchFilterMenu.classNames
  await t

    // ouverture du filtre
    .click(toogleFilterButton)

    .expect(classFilterDiv)
    .contains('transition-status-entered')

    // changement de l'icône
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-chevron-up')

    // fermeture du filtre
    .click(toogleFilterButton)

    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')

    .expect(classFilterDiv)
    .contains('transition-status-exited')
})
