import { Role } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

import { offererUser } from './users'

export const regularOfferer = Role(ROOT_PATH+'connexion', async t => {
  await t
    .typeText('#sign-in-identifier', offererUser.email)
    .typeText('#sign-in-password', offererUser.password)
    .wait(1000)
    .click('button.button.is-primary')
    .wait(1000)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/offres')
},
{ preserveUrl: true
})
