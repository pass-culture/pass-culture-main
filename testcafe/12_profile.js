import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'

const profilPath = `${ROOT_PATH}profil`

fixture('Étant connecté, je vais sur mon compte,').beforeEach(async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )

  await t.useRole(userRole).navigateTo(profilPath)
})

test(`je clique sur le lien pour accéder au formulaire de mes informations personnelles,
    je saisis un pseudo de moins de 3 caracteres et j'ai un message d'erreur à la soumission,
    puis je modifie mon pseudo pour qu'il soit correct,
    je le soumet et j'arrive sur mon profil.`, async t => {

  const personalInformationsPath = `${ROOT_PATH}profil/informations`
  const personalInformationsLink = Selector('a').withText('Informations personnelles')
  const nicknameInput = Selector('input[name="publicName"]')
  const newNickname = 'aa'
  const validNickname = 'pseudo different'
  const emptyField = 'ctrl+a delete'
  const submitInput = Selector('input[type="submit"]')
  const errorMessage = Selector('p').withText('Vous devez saisir au moins 3 caractères.')
  const updatedNickname = Selector('main').withText(validNickname)

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
    .click(nicknameInput)
    .pressKey(emptyField)
    .typeText(nicknameInput, validNickname)
    .click(submitInput)
    .expect(getPageUrl())
    .contains(profilPath)
    .expect(updatedNickname.exists)
    .ok()
})
