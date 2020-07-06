import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'

import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'

const showVerso = Selector('button.button.to-recto')
const discoveryPage = Selector('.discovery-page')
const favoriButton = Selector('button.fav-button')
const button = Selector('button')
const section = Selector('.teaser-item')
const favoriteBoxes = section.find('.teaser-link')

let userRole
let user
let favoriteOfferName

fixture('En consultant la liste de mes favoris').beforeEach(async t => {
  userRole = await fetchSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_event_offer'
  )
  user = userRole.user

  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}decouverte`)
  await t.click(showVerso)
  favoriteOfferName = await discoveryPage.find('h1').textContent
  await t.click(favoriButton)
})

test("j'ai un encart pour chacun de mes favoris", async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}favoris`)

  // then
  await t.expect(favoriteBoxes.nth(-1).find('.teaser-title').textContent).eql(favoriteOfferName)
})

test('je peux supprimer un favori', async t => {
  // given
  await t.navigateTo(`${ROOT_PATH}favoris`)

  const modifyButton = button.withText('Modifier')
  await t.click(modifyButton)

  const lastCheckbox = favoriteBoxes.find('input').withAttribute('type', 'checkbox')
  await t.click(lastCheckbox)

  const intialNumberOfFavorites = await favoriteBoxes.count

  // when
  const deleteButton = button.withText('Supprimer')
  await t.click(deleteButton)

  // then
  const newNumberOfFavorites = favoriteBoxes.count
  await t.expect(newNumberOfFavorites).eql(intialNumberOfFavorites - 1)
})
