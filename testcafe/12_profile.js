import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'

fixture('Quand je navigue vers /profil,').beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )

  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}profil`)
})

test('je vois le lien vers Informations Personnelles', async t => {
  const personalInformationsLink = Selector('a').withText('Informations personnelles')

  await t.expect(personalInformationsLink.exists).ok()
})

test('je suis redirigé.e vers /profil/informations quand je clique sur Informations Personnelles', async t => {
  const personalInformationsLink = Selector('a').withText('Informations personnelles')

  await t.click(personalInformationsLink)

  const location = await t.eval(() => window.location)

  const personalInformationsHeader = Selector('header').withText('Informations personnelles')

  const personalInformationsFields = Selector('label').count

  const submitButton = Selector('button').withText('Enregistrer')

  await t
    .expect(location.pathname)
    .contains('/profil/informations')
    .expect(personalInformationsHeader.exists)
    .ok()
    .expect(personalInformationsFields)
    .eql(4)
    .expect(submitButton.exists)
    .ok()
})
