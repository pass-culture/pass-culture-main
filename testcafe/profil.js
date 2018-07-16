import { Selector, RequestLogger } from 'testcafe'

import regularUser from './helpers/roles'
import BROWSER_ROOT_URL from './helpers/config'

const logger = RequestLogger(BROWSER_ROOT_URL+'recommendations?occasionType=Event&occasionId=', {
    logResponseBody: true,
    stringifyResponseBody: true,
    logRequestBody: true,
    stringifyRequestBody: true
  })


fixture `Modale Profil`
  .requestHooks(logger)

    const profileButton = Selector('button')
    const profileModal= Selector('.modal')

  test("Lorsque l'utilisateur clique sur l'icone profil, la modale s'affiche", async t => {
      await t
      .useRole(regularUser)
      await t.navigateTo(BROWSER_ROOT_URL+'tuto/AE')

      const location = await t.eval(() => window.location)
      console.log('locarion ---- ', location)
      // await t.expect(Selector('header').innerText).eql('Mon profil')

      // console.log('loggerMessages', logger.requests)
      // .click(profileButton)
      await t.click('.button')
      // .wait(1000)
      await t.expect(profileModal.visible).ok()
  })
