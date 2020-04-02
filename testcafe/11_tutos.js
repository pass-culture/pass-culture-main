import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import { fetchSandbox } from './helpers/sandboxes'

fixture('Quand je navigue vers /bienvenue,').beforeEach(async t => {
  t.ctx.sandbox = await fetchSandbox(
    'webapp_02_signin',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )

  await t.navigateTo(`${ROOT_PATH}bienvenue`)
})

test('je vois le texte de la première carte tutoriel', async t => {
  const tutoText = Selector('p').withText(
    "À partir d'aujourd'hui, tu as 2 ans et 500€ crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !"
  )

  await t.expect(tutoText.exists).ok()
})
