import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'

const profilePath = `${ROOT_PATH}profil`
const discoveryPath = `${ROOT_PATH}decouverte`
const emptyField = 'ctrl+a delete'
const submitInput = Selector('input[type="submit"]')

fixture('Étant connecté, je vais sur mon compte,').beforeEach(async t => {
  t.ctx.sandbox = await fetchSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )

  const { user } = t.ctx.sandbox
  t.ctx.user = user
  const userRole = await createUserRole(user)

  await t.useRole(userRole).navigateTo(profilePath)
})

test('je clique sur le lien pour accéder au formulaire de mes informations personnelles', async t => {
  const personalInformationsPath = `${ROOT_PATH}profil/informations`
  const personalInformationsLink = Selector('a').withText('Informations personnelles')
  const nicknameInput = Selector('input[name="publicName"]')
  const newNickname = 'aa'
  const validNickname = 'pseudo different'
  const errorMessage = Selector('pre').withText('Tu dois saisir au moins 3 caractères.')
  const updatedNickname = Selector('main').withText(validNickname)

  // Je saisis un pseudo invalide et j'ai un message d'erreur
  await t
    .click(personalInformationsLink)
    .expect(getPageUrl())
    .contains(personalInformationsPath)
    .click(nicknameInput)
    .pressKey(emptyField)
    .typeText(nicknameInput, newNickname)
    .click(submitInput)
    .expect(errorMessage.exists)
    .ok()

  // Je modifie mon pseudo pour le rendre valide et je suis redirigé vers mon profil à la soumission
  await t
    .click(nicknameInput)
    .pressKey(emptyField)
    .typeText(nicknameInput, validNickname)
    .click(submitInput)
    .expect(getPageUrl())
    .contains(profilePath)
    .expect(updatedNickname.exists)
    .ok()
})

test('je clique sur le lien pour accéder au formulaire de changement de mot de passe', async t => {
  const passwordPath = `${ROOT_PATH}profil/mot-de-passe`
  const passwordLink = Selector('a').withText('Mot de passe')
  const currentPasswordInput = Selector('input').nth(0)
  const newPasswordInput = Selector('input').nth(1)
  const newConfirmationPasswordInput = Selector('input').nth(2)
  const userCurrentPassword = 'user@AZERTY123'
  const userNewPassword = 'user@AZERTY1234'
  const weakPassword = 'weak'
  const incorrectPassword = 'incorrect password'
  const signoutLink = Selector('a').withText('Déconnexion')
  const userEmailInput = Selector('input[type="email"]')
  const userPasswordInput = Selector('input[type="password"]')
  const signInButton = Selector('button[type="submit"]')
  const { email } = t.ctx.user

  const incorrectPasswordErrorMessage = Selector('pre').withText(
    'Ton ancien mot de passe est incorrect.'
  )
  const samePasswordErrorMessage = Selector('pre').withText(
    'Ton nouveau mot de passe est identique à l’ancien.'
  )

  const weakPasswordErrorMessage = Selector('pre').withText(
    'Ton mot de passe doit contenir au moins :\n- 12 caractères\n- Un chiffre\n- Une majuscule et une minuscule\n- Un caractère spécial'
  )

  // Je rentre un ancien mot de passe incorrect et j'ai un message d'errreur
  await t
    .click(passwordLink)
    .expect(getPageUrl())
    .contains(passwordPath)
    .typeText(currentPasswordInput, incorrectPassword)
    .typeText(newPasswordInput, userNewPassword)
    .typeText(newConfirmationPasswordInput, userNewPassword)
    .click(submitInput)
    .expect(incorrectPasswordErrorMessage.exists)
    .ok()

  // Je rentre un nouveau mot de passe égal à l'ancien et j'ai un message d'erreur
  await t
    .click(currentPasswordInput)
    .pressKey(emptyField)
    .typeText(currentPasswordInput, userCurrentPassword)
    .click(newPasswordInput)
    .pressKey(emptyField)
    .typeText(newPasswordInput, userCurrentPassword)
    .click(newConfirmationPasswordInput)
    .pressKey(emptyField)
    .typeText(newConfirmationPasswordInput, userCurrentPassword)
    .click(submitInput)
    .expect(samePasswordErrorMessage.exists)
    .ok()

  // Je rentre un nouveau mot de passe trop faible et j'ai un message d'erreur
  await t
    .click(newPasswordInput)
    .pressKey(emptyField)
    .typeText(newPasswordInput, weakPassword)
    .click(newConfirmationPasswordInput)
    .pressKey(emptyField)
    .typeText(newConfirmationPasswordInput, weakPassword)
    .click(submitInput)
    .expect(weakPasswordErrorMessage.exists)
    .ok()

  // Je remplis le formulaire en respectant les règles métier et je suis redirigé vers mon profil
  await t
    .click(newPasswordInput)
    .pressKey(emptyField)
    .typeText(newPasswordInput, userNewPassword)
    .click(newConfirmationPasswordInput)
    .pressKey(emptyField)
    .typeText(newConfirmationPasswordInput, userNewPassword)
    .click(submitInput)
    .expect(getPageUrl())
    .contains(profilePath)

  // Je me déconnecte et je peux me reconnecter avec mon nouveau mot de passe définit au préalable
  await t
    .click(signoutLink)
    .typeText(userEmailInput, email)
    .typeText(userPasswordInput, userNewPassword)
    .click(signInButton)
    .expect(getPageUrl())
    .contains(discoveryPath)
})
