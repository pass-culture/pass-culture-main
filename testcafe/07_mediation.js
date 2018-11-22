import { Selector } from 'testcafe'

import { validatedOffererUserRole } from './helpers/roles'

const addMediationAnchor = Selector('a.button').withText('Ajouter une accroche')
const creditInput = Selector('#mediation-credit')
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
    .useRole(validatedOffererUserRole)
    .click(editOfferAnchor)

    .click(addMediationAnchor)

  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/offres\/([A-Z0-9]*)\/accroches\/nouveau$/)
})

test('Je peux charger une image same origin', async t => {
  await t
    .useRole(validatedOffererUserRole)
    .click(editOfferAnchor)

    .click(addMediationAnchor)

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')

    .click(urlButton)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux charger une cors image', async t => {
  await t
    .useRole(validatedOffererUserRole)
    .click(editOfferAnchor)

    .click(addMediationAnchor)

  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )

    .click(urlButton)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux changer d image chargee', async t => {
  await t
    .useRole(validatedOffererUserRole)
    .click(editOfferAnchor)

    .click(addMediationAnchor)

  await t
    .typeText(urlInput, '/images/mediation-test.jpg')

    .click(urlButton)

    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370',
      { replace: true }
    )
    .click(urlButton)

  await t.expect(dropZoneDiv).ok()
})

test('Je peux creer une accroche', async t => {
  await t
    .useRole(validatedOffererUserRole)
    .click(editOfferAnchor)

    .click(addMediationAnchor)

  await t
    .typeText(
      urlInput,
      'https://www.deridet.com/photo/art/grande/8682609-13705793.jpg?v=1450665370'
    )
    .click(urlButton)

  await t.typeText(creditInput, 'deridet').click(submitButton)
})
