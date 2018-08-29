import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const addMediationAnchor = Selector('a.button').withText('Ajouter une accroche')
const creditInput = Selector('#mediation-credit')
const dragAndDropDiv = Selector('div.drag-n-drop')
const dropZoneDiv = Selector('div.dropzone').filterVisible()
const editOfferAnchor = Selector('a.name').withText(
  'Rencontre avec Franck Lepage'
)
const submitButton = Selector('button.button.is-primary').withText('Valider')

const urlInput = Selector("input[placeholder='URL du fichier']")
const urlButton = Selector('button.is-primary').withText('OK')

fixture`07_01 MediationPage | Naviguer vers ajouter une accroche`

test("Lorsque je clique sur le bouton créer une accroche sur la page d'une offre, j'accède au formulaire de création d'une accroche", async t => {
  await t
    .useRole(regularOfferer)
    .click(editOfferAnchor)
    .wait(500)
    .click(addMediationAnchor)
    .wait(500)

  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/offres\/([A-Z0-9]*)\/accroches\/nouveau$/)
})

test('Je peux charger une image same origin', async t => {
  await t
    .useRole(regularOfferer)
    .click(editOfferAnchor)
    .wait(500)
    .click(addMediationAnchor)
    .wait(500)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')
    .wait(500)
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux charger une cors image', async t => {
  await t
    .useRole(regularOfferer)
    .click(editOfferAnchor)
    .wait(500)
    .click(addMediationAnchor)
    .wait(500)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .wait(500)
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux changer d image chargee', async t => {
  await t
    .useRole(regularOfferer)
    .click(editOfferAnchor)
    .wait(500)
    .click(addMediationAnchor)
    .wait(500)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')
    .wait(500)
    .click(urlButton)
    .wait(500)
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370',
      { replace: true }
    )
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux creer une accroche', async t => {
  await t
    .useRole(regularOfferer)
    .click(editOfferAnchor)
    .wait(500)
    .click(addMediationAnchor)
    .wait(500)

  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)
    .wait(500)

  await t
    .typeText(creditInput, 'deridet')
    .click(submitButton)
    .wait(5000)
})
