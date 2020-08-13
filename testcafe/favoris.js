import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

fixture('Favoris,')

test('je peux ajouter une offre à mes favoris et supprimer une offre de mes favoris', async t => {
  const userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_event_offer'
  )
  const showVerso = Selector('button.button.to-recto')
  const discoveryPage = Selector('.discovery-page')
  const favoriButton = Selector('button.fav-button')
  const favoriteBoxes = Selector('li .teaser-link')
  const lastCheckbox = favoriteBoxes.find('input').withAttribute('type', 'checkbox')
  const button = Selector('button')
  const modifyButton = button.withText('Modifier')
  const deleteButton = button.withText('Supprimer')

  await t.useRole(userRole).navigateTo(`${ROOT_PATH}decouverte`)

  // je peux ajouter une offre à mes favoris via le carrousel
  const favoriteOfferName = await discoveryPage.find('h1').textContent
  await t.click(showVerso).click(favoriButton)

  // je vais sur mes favoris, je vérifie qu'il est là et je peux le supprimer
  await t
    .navigateTo(`${ROOT_PATH}favoris`)
    .expect(favoriteBoxes.nth(-1).withText(favoriteOfferName))
    .ok()
    .click(modifyButton)
    .click(lastCheckbox)
  const initialNumberOfFavorites = await favoriteBoxes.count
  await t.click(deleteButton)
  const newNumberOfFavorites = favoriteBoxes.count
  await t.expect(newNumberOfFavorites).eql(initialNumberOfFavorites - 1)
})
