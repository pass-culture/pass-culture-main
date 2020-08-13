import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'

fixture('Suite à l’activation de mon compte,')

test('je me connecte et j’accède à la page d’accueil', async t => {
  const userPassword = Selector('#user-password')
  const userIdentifier = Selector('#user-identifier')
  const identifierErrors = Selector('#user-identifier-error').find('.pc-error-message')
  const signInButton = Selector('#sign-in-button')
  const {
    user: { email, password },
  } = await fetchSandbox(
    'webapp_02_signin',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )

  await t
    .navigateTo(`${ROOT_PATH}connexion`)
    .typeText(
      userIdentifier,
      email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText(userPassword, password)
    .click(signInButton)
    .expect(identifierErrors.count)
    .eql(0)
    .expect(getPageUrl())
    .contains('/accueil')
})
