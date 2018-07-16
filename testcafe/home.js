import { Selector } from 'testcafe'

import BROWSER_ROOT_URL from './helpers/config'

fixture `BetaPage | Arrivée d'un nouvel utilisateur à la racine de la webapp`
    .page `${BROWSER_ROOT_URL}`

test('Le nouvel utilisateur est redirigé vers /beta', async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/beta')
})

test("Lorsque le nouvel utilisateur clique sur le bouton, il est redirigé vers la page /inscription", async t => {
    await t
      .expect(Selector('.button').innerText)
      .eql('C\'est par là')
      .click('.button')
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/inscription')
})
