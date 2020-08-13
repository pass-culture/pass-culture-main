import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'

fixture('Sur le carrousel,')

test('je peux naviguer', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_03_decouverte',
    'get_existing_webapp_user_with_bookings'
  )
  const currentCard = Selector('div.card.current')
  const nextButton = Selector('button.button.after')
  const previousButton = Selector('button.button.before')
  const showVerso = Selector('button.button.to-recto')
  const versoDiv = Selector('div.verso')
  const closeVersoLink = Selector('#deck .close-link')
  const bookingButton = Selector('button').withText('J’y vais !')
  const favoriteButton = Selector('button img').withAttribute('alt', 'Ajouter aux favoris')
  const shareButton = Selector('button img').withAttribute('alt', 'Partager cette offre')
  const urlAtStart = getPageUrl()

  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}decouverte`)

    // je peux parcourir les offres de gauche à droite et de droite à gauche
    .expect(nextButton.visible)
    .ok()
    .drag(currentCard, -200, 0)
    .expect(getPageUrl())
    .notEql(urlAtStart)
    .expect(previousButton.visible)
    .ok()
    .drag(currentCard, 200, 0)
    .expect(getPageUrl())
    .notEql(urlAtStart)

    // je peux afficher le verso des cartes en cliquant sur le bouton "haut"
    .click(showVerso)
    .expect(versoDiv.hasClass('flipped'))
    .ok()
    .click(closeVersoLink)
    .expect(versoDiv.hasClass('flipped'))
    .notOk()

    // je peux afficher/cacher le verso des cartes en glissant vers le haut/bas
    .drag(currentCard, 0, -100)
    .expect(versoDiv.hasClass('flipped'))
    .ok()
    .drag(currentCard, 0, 80)
    .expect(versoDiv.hasClass('flipped'))
    .notOk()

    // je ne peux pas cacher le verso d’une carte en glissant vers le bas si je commence sur un bouton
    .drag(currentCard, 0, -100)
    .drag(bookingButton, 0, 10)
    .drag(favoriteButton, 0, 10)
    .drag(shareButton, 0, 10)
    .expect(versoDiv.hasClass('flipped'))
    .ok()
})
