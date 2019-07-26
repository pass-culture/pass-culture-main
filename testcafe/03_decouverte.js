import { Selector } from 'testcafe'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const currentCard = Selector('div.card.current')
const nextButton = Selector('button.button.after')
const previousButton = Selector('button.button.before')
const showVerso = Selector('button.button.to-recto')
const versoDiv = Selector('div.verso')
const closeVersoLink = Selector('#deck .close-link')

let userRole

fixture('Sur la page découverte,').beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_03_decouverte',
      'get_existing_webapp_user_with_bookings'
    )
  }
  await t.useRole(userRole)
})

test('Je peux parcourir les offres de gauche à droite et de droite à gauche', async t => {
  await t.navigateTo(`${ROOT_PATH}decouverte`)
  await t.expect(nextButton.visible).ok()

  const urlAtStart = getPageUrl()
  await t.drag(currentCard, -100, 0)
  await t.expect(getPageUrl()).notEql(urlAtStart)
  await t.expect(previousButton.visible).ok()

  await t.drag(currentCard, 100, 0)
  await t.expect(getPageUrl()).notEql(urlAtStart)
})

test('Je peux afficher le verso des cartes en cliquant sur le bouton "haut"', async t => {
  await t.click(showVerso)
  await t.expect(versoDiv.hasClass('flipped')).ok()
  await t.click(closeVersoLink)
  await t.expect(versoDiv.hasClass('flipped')).notOk()
})

test('Je peux afficher/cacher le verso des cartes en glissant vers le haut/bas', async t => {
  await t.drag(currentCard, 0, -100)
  await t.expect(versoDiv.hasClass('flipped')).ok()

  await t.drag(currentCard, 0, 100)
  await t.expect(versoDiv.hasClass('flipped')).notOk()
})
