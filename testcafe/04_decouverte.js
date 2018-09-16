import { Selector, ClientFunction } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import regularUser from './helpers/roles'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const nextButton = Selector('button.button.after')
const showVerso = Selector('button.button.to-recto')
const versoDiv = Selector('div.verso')
const clueDiv = Selector('div.clue')
const closeButton = Selector('.close-button')
// // const spanPrice  = Selector('.price')
// const draggableImage = Selector('.react-draggable')

fixture('O4_01 Découverte | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}decouverte`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t
  // const location = await t.eval(() => window.location)
  // await t.expect(location.pathname).eql('/connexion')
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 10000 })
})

fixture(
  'O4_02 Découverte | Après connexion | Les offres sont en cours de chargement'
).beforeEach(async t => {
  await t.useRole(regularUser)
})

test('Je suis informé·e du fait que les offres sont en cours de chargement', async t => {
  await t
    .expect(Selector('.loading').innerText)
    .eql('\nchargement des offres\n')
})

test('Je suis redirigé·e vers la première page de tutoriel /decouverte/tuto/AE', async t => {
  await t.wait(1000)
  // test instable, reste par moment sur decouverte... Voir si location ne garderait pas la valeur du précédant test...
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/decouverte/tuto/AE')
})

test('Lorsque je clique sur la flêche suivante, je vois la page suivante du tutoriel', async t => {
  await t.click(nextButton).wait(1000)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/decouverte/tuto/A9')
})

test('Lorsque je clique sur la flêche vers le haut, je vois le verso de la recommendation et je peux la fermer', async t => {
  await t
    .navigateTo(ROOT_PATH + 'decouverte/tuto/A9') // eslint-disable-line
    .wait(1000)
  await t
    .expect(clueDiv.visible)
    .ok()
    .click(showVerso)
    .wait(1000)
    .expect(versoDiv.hasClass('flipped'))
    .ok()
    .click(closeButton)
    .expect(versoDiv.hasClass('flipped'))
    .notOk()
})

fixture('O4_03 Découverte | Après connexion | Recommandations').beforeEach(
  async t => {
    await t.useRole(regularUser)
    await t.navigateTo(ROOT_PATH + 'decouverte/AH7Q/AU#AM') // eslint-disable-line
  }
)

test.skip("Je vois les informations de l'accroche du recto", async t => {
  await t
  // TODO
})

test('Je vois le verso des cartes lorsque je fais glisser la carte vers le haut', async t => {
  await t.click(showVerso).wait(1000)
  await t.expect(versoDiv.find('h1').innerText).eql('Vhils')
  await t.expect(versoDiv.find('h2').innerText).eql('LE CENTQUATRE-PARIS')
  // TODO
})

// TODO tester le drag des images https://devexpress.github.io/testcafe/documentation/test-api/actions/drag-element.html
