import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import { fetchSandbox } from './helpers/sandboxes'

fixture('Favoris,')

test('je peux ajouter une offre à mes favoris et supprimer une offre de mes favoris', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_event_offer'
  )
  const { offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )

  const offerPageElement = Selector('.offer-page')
  const favoriButton = Selector('button.fav-button')
  const favoriteBoxes = Selector('li .teaser-link')
  const lastCheckbox = favoriteBoxes.find('input').withAttribute('type', 'checkbox')
  const button = Selector('button')
  const modifyButton = button.withText('Modifier')
  const deleteButton = button.withText('Supprimer')

  // Je peux naviguer jusqu'au détail d'une offre
  const offerPage = `${ROOT_PATH}offre/details/${offer.id}`
  await t.useRole(userRole).navigateTo(offerPage)

  // je peux ajouter une offre à mes favoris
  const favoriteOfferName = await offerPageElement.find('h1').textContent
  await t.click(favoriButton)

  // je vais sur mes favoris, je vérifie qu'il est là et je peux le supprimer
  await t
    .navigateTo(`${ROOT_PATH}favoris`)
    .expect(favoriteBoxes.nth(-1).withText(favoriteOfferName).exists)
    .ok()
    .click(modifyButton)
    .click(lastCheckbox)
  const initialNumberOfFavorites = await favoriteBoxes.count
  await t.click(deleteButton)
  const newNumberOfFavorites = favoriteBoxes.count
  await t.expect(newNumberOfFavorites).eql(initialNumberOfFavorites - 1)
})
