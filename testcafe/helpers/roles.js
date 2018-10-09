import { Role } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

import { offererUser, adminUser } from './users'

export const regularOfferer = Role(
  ROOT_PATH + 'connexion',
  async t => {
    await t
      .typeText('#user-identifier', offererUser.email)
      .typeText('#user-password', offererUser.password)

      .click('button.button.is-primary')

    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/offres')
  },
  {
    preserveUrl: true,
  }
)

export const admin = Role(
  ROOT_PATH + 'connexion',
  async t => {
    await t
      .typeText('#user-identifier', adminUser.email)
      .typeText('#user-password', adminUser.password)
      .click('button.button.is-primary')
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/offres')
  },
  {
    preserveUrl: true,
  }
)
