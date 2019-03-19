import { ROOT_PATH } from '../src/utils/config'

fixture`Home A | J'arrive à la racine du portail pro`.page`${ROOT_PATH}`

test('Je suis redirigé·e vers la page de connexion /connexion', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
