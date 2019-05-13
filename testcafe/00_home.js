import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

fixture("00 BetaPage Component | J'arrive à la racine de la webapp").page(
  `${ROOT_PATH}`
)

test('Je suis redirigé·e vers /beta', async t => {
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/beta')
})

test('Lorsque je clique sur la flèche, je suis redirigé·e vers la page /connexion', async t => {
  const button = Selector('#beta-connexion-link')
  await t.click(button).wait(1000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
