import { Selector } from 'testcafe'

import { BROWSER_ROOT_URL } from './helpers/config'

const siretInput = Selector('#input_offerers_siren')
const submitButton  = Selector('button.button.is-primary') //connexion

fixture `VenuePage | Créer un nouveau lieu`
    .page `${BROWSER_ROOT_URL+'lieux/nouveau'}`

test("Je rentre une nouvelle structure via son siren", async t => {
  await t
    .typeText(siretInput, '692 039 514')
    .wait(1000)
    .click(submitButton)
    .wait(1000)
})
