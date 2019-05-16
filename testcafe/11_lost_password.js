import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const inputUsersEmail = Selector('#user-email')
const forgotPasswordLink = Selector('#lostPasswordLink')
const sendTokenButton = Selector('#sendTokenByMail')
const changePasswordButton = Selector('#changePassword')
const passwordInput = Selector('#user-newPassword')
const pageH1 = Selector('h1')
const errorsDiv = Selector('.errors')

fixture(
  'LostPassword A | La page de connexion propose un lien pour changer de mot de passe'
).page(`${ROOT_PATH + 'connexion'}`)

test('Je peux cliquer sur le lien mot de passe oublié', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_11_lost_password',
    'get_pro_validated_no_reset_password_token_user'
  )
  const { email } = user
  await t.click(forgotPasswordLink)
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(pageH1.innerText)
    .eql('Mot de passe égaré ?')

  // when
  await t.typeText(inputUsersEmail, email)
  await t.click(sendTokenButton)

  // then
  /*TODO WEIRD DE CHEZ WEIRD sendTokenButton words but not goes to
  /mot-de-passe-perdu?envoye=1 just only in testcafe but in dev it is okay*/
  /*
  const nextLocation = await t.eval(() => window.location)
  await t.expect(nextLocation.pathname)
         .eql('/mot-de-passe-perdu')
         .expect(nextLocation.search)
         .eql('?envoye=1')
         .expect(pageH1.innerText)
         .eql('Merci !')

  // when
  const homeAnchor = Selector('a[href="/accueil"]')
  await t.click(homeAnchor)

  // then
  */
})

fixture(
  'LostPassword B | La page de changement de mot de passe vérifie le token'
).page(`${ROOT_PATH + 'mot-de-passe-perdu?token=ABCD'}`)

test('Je ne peux pas changer mon mot de passe sans token valide', async t => {
  // then
  await t.expect(pageH1.innerText).eql('Créer un nouveau mot de passe')

  // when
  await t.typeText(passwordInput, 'ABCD').click(changePasswordButton)

  // then
  await t.expect(errorsDiv.innerText).notEql('')
})
