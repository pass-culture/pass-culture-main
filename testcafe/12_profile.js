import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'

fixture('Quand je navigue vers Mon Compte,').beforeEach(async t => {
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

test('je vois le lien vers Mot de Passe', async t => {
  const passwordLink = Selector('a').withText('Mot de passe')

  await t.expect(passwordLink.exists).ok()
})

test('je suis redirigé.e vers la page Informations personnelles quand je clique sur le lien Informations Personnelles', async t => {
  const personalInformationsLink = Selector('a').withText('Informations personnelles')

  await t.click(personalInformationsLink)

  const location = await t.eval(() => window.location)

  await t.expect(location.pathname).contains('/profil/informations')
})

test('quand je suis sur la page Informations Personnelles et que je clique sur Enregistrer, je suis redirigé.e vers Mon Compte', async t => {
  const personalInformationsLink = Selector('a').withText('Informations personnelles')

  await t.click(personalInformationsLink)

  const submitButton = Selector('button').withText('Enregistrer')

  await t.click(submitButton)

  const location = await t.eval(() => window.location)

  await t.expect(location.pathname).contains('/profil')
})

test('je suis redirigé.e vers la page Mot de passe quand je clique sur le lien Mot de passe', async t => {
  const passwordLink = Selector('a').withText('Mot de passe')

  await t.click(passwordLink)

  const location = await t.eval(() => window.location)

  await t.expect(location.pathname).contains('/profil/password')
})
