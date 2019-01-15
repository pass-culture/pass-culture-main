// testcafe chrome ./testcafe/11_activation.js
import { ROOT_PATH } from '../src/utils/config'

fixture("11 Activation Component | J'arrive à la racine d'activation").page(
  `${ROOT_PATH}activation`
)

test('Je suis redirigé·e vers /activation/error', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/activation/error')
})

fixture("11 Activation Component | l'URL n'existe pas").page(
  `${ROOT_PATH}activation/fake`
)

test('Je suis redirigé·e vers /activation/error', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/activation/error')
})
