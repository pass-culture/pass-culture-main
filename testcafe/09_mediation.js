import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewMediationAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'

const creditInput = Selector('#mediation-credit')
const editorZoneDiv = Selector('div.editor-zone').filterVisible()
const submitButton = Selector('button.primary-button').withText('Valider')
const imageUrlInput = Selector("input[placeholder='URL du fichier']")
const imageUrlButton = Selector('button.primary-button').withText('OK')
const urlInput = Selector("input[placeholder='URL du fichier']")
const urlButton = Selector('button.primary-button').withText('OK')

let userRole
let dataFromSandbox
fixture('En étant sur la page de gestion des médiations').beforeEach(async () => {
  dataFromSandbox = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  userRole = createUserRole(dataFromSandbox.user)
})

test("Lorsque je clique sur le bouton 'créer une accroche' sur la page d'une offre, j'accède au formulaire de création d'une accroche", async t => {
  // when
  const { offer, user } = dataFromSandbox
  await navigateToNewMediationAs(user, offer, userRole)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/offres\/([A-Z0-9]*)\/accroches\/nouveau$/)
})

test('Je peux créer une accroche', async t => {
  // given
  const mediationsListItems = Selector('.mediations-list li')
  const successBanner = Selector('.notification.is-success')
  const { offer, user } = dataFromSandbox
  await navigateToNewMediationAs(user, offer, userRole)(t)
  await t
    .typeText(urlInput, 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Zebra_%28PSF%29.png')
    .click(urlButton)
    .typeText(creditInput, 'wikipedia')
    .wait(10000)

  // when
  await t.click(submitButton)

  // then
  await t
    .expect(mediationsListItems.count)
    .eql(1)
    .expect(successBanner.exists)
    .ok()
})

test('Je peux charger une image same origin', async t => {
  // given
  const { offer, user } = dataFromSandbox
  await navigateToNewMediationAs(user, offer, userRole)(t)

  // when
  await t.typeText(imageUrlInput, '/images/mediation-test.jpg').click(imageUrlButton)

  // then
  await t.expect(editorZoneDiv.exists).ok()
})

test('Je peux charger une CORS image', async t => {
  // given
  const { offer, user } = dataFromSandbox
  await navigateToNewMediationAs(user, offer, userRole)(t)

  // when
  await t
    .typeText(
      imageUrlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(imageUrlButton)

  // then
  await t.expect(editorZoneDiv.exists).ok()
})

test("Je peux changer d'image chargée", async t => {
  // given
  const { offer, user } = dataFromSandbox
  await navigateToNewMediationAs(user, offer, userRole)(t)
  await t.typeText(urlInput, '/images/mediation-test.jpg').click(urlButton)

  // when
  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370',
      { replace: true }
    )
    .click(urlButton)

  // then
  await t.expect(editorZoneDiv.exists).ok()
})
