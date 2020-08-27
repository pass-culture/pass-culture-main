import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewMediationAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { getPathname } from './helpers/location'

fixture('Médiations,')

test('en étant sur la page de gestion des médiations', async t => {
  const dataFromSandbox = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  const userRole = createUserRole(dataFromSandbox.user)
  const { offer, user } = dataFromSandbox
  const creditInput = Selector('#mediation-credit')
  const editorZoneDiv = Selector('div.editor-zone').filterVisible()
  const submitButton = Selector('button').withText('Valider')
  const imageUrlInput = Selector("input[placeholder='URL du fichier']")
  const imageUrlButton = Selector('button').withText('OK')
  const urlInput = Selector("input[placeholder='URL du fichier']")
  const urlButton = Selector('button').withText('OK')
  const mediationsListItems = Selector('.mediations-list li')
  const successBanner = Selector('.notification.is-success')
  await navigateToNewMediationAs(user, offer, userRole)(t)

  // Lorsque je clique sur le bouton "créer une accroche" sur la page d'une offre, j'accède au formulaire de création d'une accroche
  await t.expect(getPathname()).match(/offres\/([A-Z0-9]*)\/accroches\/nouveau$/)

  // Je peux créer une accroche
  await t
    .typeText(urlInput, 'https://upload.wikimedia.org/wikipedia/commons/f/f9/Zebra_%28PSF%29.png')
    .click(urlButton)
    .typeText(creditInput, 'wikipedia')
    .click(submitButton)
    .expect(mediationsListItems.count)
    .eql(1)
    .expect(successBanner.exists)
    .ok()

  // Je peux charger une image same origin
  await navigateToNewMediationAs(user, offer, userRole)(t)
  await t
    .typeText(imageUrlInput, '/images/mediation-test.jpg')
    .click(imageUrlButton)
    .expect(editorZoneDiv.exists)
    .ok()

  // Je peux charger une CORS image
  await navigateToNewMediationAs(user, offer, userRole)(t)
  await t
    .typeText(
      imageUrlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(imageUrlButton)
    .expect(editorZoneDiv.exists)
    .ok()

  // Je peux changer d'image chargée
  await t
    .typeText(urlInput, '/images/mediation-test.jpg')
    .click(urlButton)
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370',
      { replace: true }
    )
    .click(urlButton)
    .expect(editorZoneDiv.exists)
    .ok()
})
