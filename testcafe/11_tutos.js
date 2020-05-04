import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let userRole

fixture('Quand je navigue vers /bienvenue,').beforeEach(async t => {
  userRole = await createUserRoleFromUserSandbox(
    'webapp_11_tutos',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )
  await t.useRole(userRole)

  await t.navigateTo(`${ROOT_PATH}bienvenue`)
})

test('je vois le texte de la première carte tutoriel', async t => {
  const tutoText = Selector('p').withText(
    'À partir d’aujourd’hui, tu as 2 ans et 500 € crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
  )

  await t.expect(tutoText.exists).ok()
})

test('je vois le texte de la deuxième carte tutoriel en cliquant sur la flèche de la première', async t => {
  const nextArrow = Selector('img').withAttribute('alt', 'Suivant')

  await t.click(nextArrow)

  const secondTutoFirstText = Selector('p')
    .nth(0)
    .withText(
      'Profite de ces 500 € en réservant sur l’appli des concerts, des cours, des abonnements à une plateforme numérique…'
    )

  const secondTutoSecondText = Selector('p')
    .nth(1)
    .withText('Psst : profite des offres duo pour inviter un ami, un voisin ou ta grand‑mère !')

  await t
    .expect(secondTutoFirstText.exists)
    .ok()
    .expect(secondTutoSecondText.exists)
    .ok()
})

test('je vois le texte de la troisième carte tutoriel en cliquant sur la flèche de la deuxième', async t => {
  let nextArrow = Selector('img').withAttribute('alt', 'Suivant')

  await t.click(nextArrow)

  nextArrow = Selector('img').withAttribute('alt', 'Suivant')

  await t.click(nextArrow)

  const thirdTutoFirstText = Selector('p')
    .nth(0)
    .withText(
      'Tu peux utiliser jusqu’à 200 € en biens physiques(livres, vinyles…) et jusqu’à 200 € en biens numériques (streaming, jeux vidéo…).'
    )
  const thirdTutoSecondText = Selector('p')
    .nth(1)
    .withText('Aucune limite sur la réservation de sorties (concerts, spectacles…) !')

  await t
    .expect(thirdTutoFirstText.exists)
    .ok()
    .expect(thirdTutoSecondText.exists)
    .ok()
})

test('je peux naviguer entre les différents tutoriels à l’aide du drag and drop', async t => {
  const firstTutorial = Selector('p').withText('À partir d’aujourd’hui')
  const secondTutorial = Selector('p')
    .nth(0)
    .withText('Profite de ces 500 €')

  await t
    .drag(firstTutorial, -200, 0)
    .expect(secondTutorial.exists)
    .ok()

  await t
    .drag(secondTutorial, 200, 0)
    .expect(firstTutorial.exists)
    .ok()
})

test("quand j'ai fini de voir le 3ème tutoriel, je suis rediriger vers une autre page", async t => {
  const nextArrow = Selector('img').withAttribute('alt', 'Suivant')
  await t.click(nextArrow)
  await t.click(nextArrow)
  await t.click(nextArrow)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('/decouverte')
})

test("quand je n'ai pas fini de voir le 3ème tutoriel, je ne peux pas naviguer sur une autre page", async t => {
  const nextArrow = Selector('img').withAttribute('alt', 'Suivant')
  await t.click(nextArrow)

  await t.navigateTo(`${ROOT_PATH}decouverte`)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/bienvenue')
})
