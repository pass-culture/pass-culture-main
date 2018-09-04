import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

fixture`00 BetaPage Component | J'arrive à la racine de la webapp` // eslint-disable-line no-unused-expressions
  .page`${ROOT_PATH}`

test('Je suis redirigé·e  vers /beta', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/beta')
})

test('Lorsque je clique sur la flêche, je suis redirigé·e  vers la page /inscription', async t => {
  await t
    .expect(Selector("a[href='/inscription']").innerText)
    .eql("C'est par là\n")
    .click('a')
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})
