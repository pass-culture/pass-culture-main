import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewMediationAs } from './helpers/navigations'

const creditInput = Selector('#mediation-credit')
const dropZoneDiv = Selector('div.dropzone').filterVisible()
const submitButton = Selector('button.button.is-primary').withText('Valider')
const urlInput = Selector("input[placeholder='URL du fichier']")
const urlButton = Selector('button.is-primary').withText('OK')

fixture('MediationPage A | Naviguer vers ajouter une accroche')

test("Lorsque je clique sur le bouton créer une accroche sur la page d'une offre, j'accède au formulaire de création d'une accroche", async t => {
  // when
  const { offer, user } = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  await navigateToNewMediationAs(user, offer)(t)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/offres\/([A-Z0-9]*)\/accroches\/nouveau$/)
})

fixture("MediationPage B | Charger des images de l'url input")

test('Je peux charger une image same origin', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  await navigateToNewMediationAs(user, offer)(t)

  // when
  await t.typeText(urlInput, '/images/mediation-test.jpg').click(urlButton)

  // then
  await t.expect(dropZoneDiv.exists).ok()
})

test('Je peux charger une cors image', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  await navigateToNewMediationAs(user, offer)(t)

  // when
  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)

  // then
  await t.expect(dropZoneDiv.exists).ok()
})

test('Je peux changer d image chargee', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  await navigateToNewMediationAs(user, offer)(t)
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
  await t.expect(dropZoneDiv.exists).ok()
})

fixture('MediationPage C | Créer une accroche')

test('Je peux créer une accroche', async t => {
  // given
  const mediationsListItems = Selector('.mediations-list li')
  const successBanner = Selector('.notification.is-success')
  const { offer, user } = await fetchSandbox(
    'pro_09_mediation',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer_with_no_mediation'
  )
  await navigateToNewMediationAs(user, offer)(t)
  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)
    .typeText(creditInput, 'deridet')
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
