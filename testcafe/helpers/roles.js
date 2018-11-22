import { Role } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

import { validatedOffererUser, adminUser0 } from './users'

export const validatedOffererUserRole = Role(
  ROOT_PATH + 'connexion',
  async t => {
    await t
      .typeText('#user-identifier', validatedOffererUser.email)
      .typeText('#user-password', validatedOffererUser.password)

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
      .typeText('#user-identifier', adminUser0.email)
      .typeText('#user-password', adminUser0.password)
      .click('button.button.is-primary')
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/offres')
  },
  {
    preserveUrl: true,
  }
)
