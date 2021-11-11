import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'

fixture('Quand je suis un nouveau bénéficiaire,')

test('je navigue à travers le tutoriel', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_11_tutos',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )
  const goForward = -200
  const goBack = 200
  const nextArrow = Selector('img').withAttribute('alt', 'Suivant')
  const tutoText = Selector('p').withText(
    'À partir d’aujourd’hui, tu as 2 ans et 500 € crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
  )
  const secondTutoFirstText = Selector('p')
    .nth(0)
    .withText(
      'Profite de ces 500 € en réservant sur l’appli des concerts, des cours, des abonnements à une plateforme numérique…'
    )
  const secondTutoSecondText = Selector('p')
    .nth(1)
    .withText('Psst : profite des offres duo pour inviter un ami, un voisin ou ta grand‑mère !')
  const thirdTutoFirstText = Selector('p')
    .nth(0)
    .withText(
      'Tu peux utiliser jusqu’à 200 € en biens physiques(livres, vinyles…) et jusqu’à 200 € en biens numériques (streaming, jeux vidéo…).'
    )
  const thirdTutoSecondText = Selector('p')
    .nth(1)
    .withText('Aucune limite sur la réservation de sorties (concerts, spectacles…) !')

  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}bienvenue`)

    // je vois le texte de la première carte tutoriel
    .expect(tutoText.exists)
    .ok()

    // je vois le texte de la deuxième carte tutoriel en cliquant sur la flèche de la première
    .click(nextArrow)
    .expect(secondTutoFirstText.exists)
    .ok()
    .expect(secondTutoSecondText.exists)
    .ok()

    // je vois le texte de la troisième carte tutoriel en cliquant sur la flèche de la deuxième
    .click(nextArrow)
    .expect(thirdTutoFirstText.exists)
    .ok()
    .expect(thirdTutoSecondText.exists)
    .ok()

    // quand je n'ai pas fini de voir le troisième tutoriel, je ne peux pas naviguer sur une autre page
    .navigateTo(`${ROOT_PATH}accueil`)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}bienvenue`)

    // je peux naviguer à l’aide du drag and drop jusqu'au troisième tutoriel
    .drag(tutoText, goForward, 0)
    .drag(secondTutoFirstText, goBack, 0)
    .drag(tutoText, goForward, 0)
    .drag(secondTutoFirstText, goForward, 0)
    .drag(thirdTutoFirstText, goForward, 0)

    // quand j'ai fini de voir le troisième tutoriel, je suis redirigé vers une autre page
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}accueil`)
})
