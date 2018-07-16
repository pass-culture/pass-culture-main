import { Selector, RequestLogger } from 'testcafe'

import BROWSER_ROOT_URL from './helpers/config'
import regularUser from './helpers/roles'

const logger = RequestLogger(BROWSER_ROOT_URL+'recommendations?occasionType=Event&occasionId=', {
    logResponseBody: true,
    stringifyResponseBody: true,
    logRequestBody: true,
    stringifyRequestBody: true
  })


fixture `Découverte | Utilisateur non loggé`
.page `${BROWSER_ROOT_URL+'decouverte'}`

  test("L'utilisateur est redirigé vers la page /connexion", async t =>
  {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
  })

fixture `Découverte | Après connexion | Les offres sont en cours de chargement`
    // .page `${BROWSER_ROOT_URL}`

     .beforeEach( async t => {
       await t
       .useRole(regularUser)
    })

    test("L'utilisateur est redirigé vers la page /decouverte", async t =>
    {
      await t
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/decouverte')
    })

    test("L'utilisateur est informé du fait que les offres sont en cours de chargement", async t => {
	   await t
     .expect(Selector('.loading').innerText).eql('\nchargement des offres\n')
     })

fixture `Découverte | Après connexion | Les offres sont chargées`
// TODO en attente d'un bug fix
// Lorsque les offres sont chargées, redirection vers /decouverte/tuto/AE
