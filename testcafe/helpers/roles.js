import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'
import youngUser from './users'

const signInButton = Selector('button').withText('Connexion')

const regularUser = Role(
  `${ROOT_PATH}connexion`,
  async t => {
    await t
      .typeText('#user-identifier', youngUser.email)
      .typeText('#user-password', youngUser.password)
      .wait(500)
      .click(signInButton)
      .wait(500)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/decouverte')
  },
  {
    preserveUrl: true,
  }
)

export default regularUser
