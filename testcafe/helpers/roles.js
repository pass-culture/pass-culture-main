import { Role } from 'testcafe'
import BROWSER_ROOT_URL from './config.js'

const regularUser = Role(BROWSER_ROOT_URL+'connexion', async t => {
    await t
        .typeText('#input_users_identifier', 'pctest.cafe@btmx.fr')
        .typeText('#input_users_password', 'password1234')
        .wait(500)
        .click('button')
        .wait(500)
},
{ preserveUrl: true
})

export default regularUser
