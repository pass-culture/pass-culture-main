import BROWSER_ROOT_URL from './helpers/config'

fixture `HomePage | Arrivée d'un nouvel utilisateur à la racine`
    .page `${BROWSER_ROOT_URL}`

test('Le nouvel utilisateur est redirigé·e vers la page de connexion /connexion', async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
})
