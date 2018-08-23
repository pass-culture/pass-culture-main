import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const dragAndDropDiv = Selector('div.drag-n-drop')
const dropZoneDiv = Selector('div.dropzone').filterVisible()
const createMediationAnchor = Selector(
  "a.button[href='/offres/A9/accroches/nouveau']"
)
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

test('Je peux créer une accroche', async t => {
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
