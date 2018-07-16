import { Role } from 'testcafe'

import BROWSER_ROOT_URL from './config.js'

const { PC_TEST_CAFE_PWD } = process.env

const regularOfferer = Role(BROWSER_ROOT_URL+'connexion', async t => {
    await t
        .typeText('#input_users_identifier', 'pctest.cafe@btmx.fr')
        .typeText('#input_users_password', PC_TEST_CAFE_PWD)
        .wait(1000)
        .click('button.button.is-primary')
        .wait(1000)
        const location = await t.eval(() => window.location)
        await t.expect(location.pathname).eql('/offres')
},
{ preserveUrl: true
})

export const newOfferer = Role(BROWSER_ROOT_URL+'inscription', async t => {
  // TODO Test faux en attendant la possibilité de créer un utilisateur à chaque test
  await t
      .typeText('#input_users_publicName', 'Public Name')
      .typeText('#input_users_email', 'pctest.cafe@btmx.fr')
      .typeText('#input_users_password', PC_TEST_CAFE_PWD)
      .typeText('#input_users_siren', '492475033')
      .click('#input_users_contact_ok')
      .wait(1000)
      .click('button.button.is-primary')
      .wait(1000)
      const location = await t.eval(() => window.location)
      await t.expect(location.pathname).eql('/toto')
},
{ preserveUrl: true
})

export default regularOfferer
