import { Role } from 'testcafe'
import { ROOT_PATH } from '../../src/utils/config'

const regularUser = Role(
  `${ROOT_PATH  }connexion`,
  async t => {
    // eslint-disable-line
    await t
      .typeText('#users_identifier', 'pctest.cafe@btmx.fr')
      .typeText('#users_password', 'password1234')
      .wait(500)
      .click('button')
      .wait(500)
  },
  {
    preserveUrl: true,
  }
)

export default regularUser
