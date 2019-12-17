import { Selector } from 'testcafe'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const userId = '#user-identifier'
const passId = '#user-password'
const errorClass = '.pc-error-message'
const userPassword = Selector(passId)
const userIdentifier = Selector(userId)
const identifierErrors = Selector(`${userId}-error`).find(errorClass)
const signInButton = Selector('#sign-in-button')

fixture("Suite à l'activation de mon compte,")
  .page(`${ROOT_PATH}connexion`)
  .beforeEach(async t => {
    t.ctx.sandbox = await fetchSandbox(
      'webapp_02_signin',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  })

test("je me connecte et j'accède à la page découverte", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user
  await t
    .typeText(
      userIdentifier,
      email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText(userPassword, password)

  // when
  await t.click(signInButton)

  // then
  await t.expect(identifierErrors.count).eql(0)
  await t.expect(getPageUrl()).contains('/decouverte')
})
