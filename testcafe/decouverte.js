import { Selector, RequestLogger } from 'testcafe'

import BROWSER_ROOT_URL from './helpers/config'
import regularUser from './helpers/roles'

const logger = RequestLogger('http://localhost/recommendations?', {
    logResponseBody: true,
    stringifyResponseBody: true,
    logRequestBody: true,
    stringifyRequestBody: true
  })

  const nextButton  = Selector('button.button.after')
  const showVerso  = Selector('button.button.to-recto')
  const versoDiv  = Selector('div.verso')
  const closeButton  = Selector('.close-button')
  const spanPrice  = Selector('.price')

fixture `Découverte | Utilisateur non loggé`
.page `${BROWSER_ROOT_URL+'decouverte'}`

  test("Je suis redirigé vers la page /connexion", async t =>
  {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
  })

fixture `Découverte | Après connexion | Les offres sont en cours de chargement`

     .beforeEach( async t => {
       await t
       .useRole(regularUser)
    })

    test("Je suis informé du fait que les offres sont en cours de chargement", async t => {
      await t
      .expect(Selector('.loading').innerText).eql('\nchargement des offres\n')
    })

    test("Je suis redirigé vers la première page de tutoriel /decouverte/tuto/AE", async t =>
    {
      await t
      // test instable, reste par moment sur decouverte... Voir si location ne garderait pas la valeur du précédant test...
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/decouverte/tuto/AE')
    })

    test('Lorsque je clique sur la flêche suivante, je vois la page suivante du tutoriel', async t => {
      await t
      .click(nextButton)
      .wait(1000)
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/decouverte/tuto/A9')
    })

fixture `Découverte | Après connexion | Les recommandations sont affichées après l'affichage du tutoriel`
  // .page `${BROWSER_ROOT_URL+'decouverte'}`
  .beforeEach( async t => {
    await t
   .useRole(regularUser)
   .navigateTo(BROWSER_ROOT_URL+'decouverte/tuto/A9')
  })

    test('Lorsque je clique sur la flêche vers le haut, je vois le verso de la recommendation et je peux la fermer', async t => {
      await t
      .wait(1000)
      .click(showVerso)
      .wait(1000)
      .expect(versoDiv.hasClass('flipped')).ok()
      .click(closeButton)
      .expect(versoDiv.hasClass('flipped')).notOk()
    })

    test('Après avoir vu les deux cartes du tutoriel, je vois la première recommandation', async t => {
      await t
      .click(nextButton)
      .wait(1000)
      const location = await t.eval(() => window.location)
      // await t.expect(location.pathname).eql('/decouverte/AJGA/AM')
      await t.expect(location.pathname).eql('/decouverte/AH7Q/AU')
      // /decouverte/AH7Q/AU'
    })


fixture `Découverte | Après connexion | Recommandations`
  .beforeEach( async t => {
    await t
   .useRole(regularUser)
   .navigateTo(BROWSER_ROOT_URL+'decouverte/AH7Q/AU#AM')
  })

  test("Je vois les informations de l'accroche du recto", async t => {
    await t
    // const location = await t.eval(() => window.location)
    // console.log('>>> location.pathname ', location.pathname)
    .wait(3000)
    await t.expect(spanPrice.innerText).eql('totot')

  })

// TODO tester le drag des images https://devexpress.github.io/testcafe/documentation/test-api/actions/drag-element.html

    // .requestHooks(logger)
