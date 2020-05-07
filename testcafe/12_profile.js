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

test('je clique sur le lien pour accéder au formulaire de mes informations personnelles et je modifie mon pseudo', async t => {
  const personalInformationsPath = `${ROOT_PATH}profil/informations`
  const personalInformationsLink = Selector('a').withText('Informations personnelles')
  const nicknameInput = Selector('input[name="publicName"]')
  const newNickname = 'pseudo different'
  const emptyField = 'ctrl+a delete'
  const submitButton = Selector('button').withText('Enregistrer')
  const updatedNickname = Selector('main').withText(newNickname)

  await t
    .click(personalInformationsLink)
    .expect(getPageUrl())
    .contains(personalInformationsPath)
    .click(nicknameInput)
    .pressKey(emptyField)
    .typeText(nicknameInput, newNickname)
    .click(submitButton)
    .expect(getPageUrl())
    .contains(profilPath)
    .expect(updatedNickname.exists)
    .ok()
})
