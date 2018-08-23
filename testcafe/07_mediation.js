import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const createMediationAnchor = Selector("a[href^='/offres/nouveau']")

const editScheduleAnchor = Selector("a.button[href='/offres/A9?gestion&date=']")

fixture`07_01 MediationPage | Naviguer vers ajouter une accroche`

test.skip("Lorsque je clique sur le bouton ajouter une accroche sur la page d'une offre, j'accède au formulaire de création d'une accroche", async t => {
  await t
    .useRole(regularOfferer)
    .click(createMediationAnchor)
    .wait(1000)

  const location = await t.eval(() => window.location)
  //await t.expect(location.pathname).eql('/offres/nouveau')
})
