import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const creditInput = Selector('#mediation-credit')
const dragAndDropDiv = Selector('div.drag-n-drop')
const dropZoneDiv = Selector('div.dropzone').filterVisible()
const createMediationAnchor = Selector(
  "a.button[href='/offres/A9/accroches/nouveau']"
)
const submitButton = Selector('button.button.is-primary').withText('Valider')

const urlInput = Selector("input[placeholder='URL du fichier']")
const urlButton = Selector('button.is-primary').withText('OK')

fixture`07_01 MediationPage | Naviguer vers ajouter une accroche`

test("Lorsque je clique sur le bouton ajouter une accroche sur la page d'une offre, j'accède au formulaire de création d'une accroche", async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/A9/accroches/nouveau')
})

test('Je peux charger une image same origin', async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux charger une cors image', async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux changer d image chargee', async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

  await t
    .expect(dragAndDropDiv.innerText)
    .eql('Cliquez ou glissez-déposez pour charger une image')

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')
    .click(urlButton)
    .wait(500)
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)
    .wait(500)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux creer une offre', async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

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
