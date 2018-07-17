import { Role } from 'testcafe'

const regularUser = Role('http://localhost:3000/connexion', async t => {
    await t
        .typeText('#input_users_identifier', 'testcafe_user@btmx.fr')
        .typeText('#input_users_password', 'password1234')
        .wait(1000)
        .click('button')
        .wait(1000)
},
{ preserveUrl: true
})

export default regularUser
