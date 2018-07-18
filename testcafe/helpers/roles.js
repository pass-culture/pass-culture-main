import { Role } from 'testcafe'
import BROWSER_ROOT_URL from './config.js'

const regularUser = Role(BROWSER_ROOT_URL+'connexion', async t => {
    await t
        .typeText('#input_users_identifier', 'pctest.cafe@btmx.fr')
        .typeText('#input_users_password', 'password1234')
        .wait(1000)
        .click('button')
        .wait(1000)
},
{ preserveUrl: true
})

export default regularUser
