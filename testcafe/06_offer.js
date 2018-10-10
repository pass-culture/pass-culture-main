import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const addScheduleAnchor = Selector('#add-occurrence-or-stock')
const availableInput = Selector('#stock-available')
const beginningDateInput = Selector('#occurrence-beginningDate')
const bookingLimitDatetimeInput = Selector('#stock-bookingLimitDatetime')
const cancelAnchor = Selector('button.button').withText('Annuler')
const createOfferAnchor = Selector("a[href^='/offres/nouveau']")
const createOfferFromVenueAnchor = Selector("a[href^='/offres/nouveau?lieu=']")
const descriptionInput = Selector('#offer-description')
const durationMinutesInput = Selector('#offer-durationMinutes')
const editScheduleAnchor = Selector(
  "a.button[href^='/offres/A9?gestion&date=']"
)
const nameInput = Selector('#offer-name')
const navbarAnchor = Selector(
  'a.navbar-link, span.navbar-burger'
).filterVisible()
const occurenceBeginningTimeInput = Selector('#occurrence-beginningTime')
const occurenceEndTimeInput = Selector('#occurrence-endTime')
const offererAnchor = Selector("a[href^='/structures/']").withText(
  'THEATRE NATIONAL DE CHAILLOT'
)
const offererInput = Selector('#offer-offererId')
const offererOption = Selector('option').withText(
  'THEATRE NATIONAL DE CHAILLOT'
)
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const priceInput = Selector('#stock-price')
const scheduleCloseButton = Selector('button.button').withText('Fermer')
const scheduleSubmitButton = Selector('button.button.submitStep')

const submitButton = Selector('button.button.is-primary').withText(
  'Enregistrer'
)
const typeOption = Selector('option').withText('Conférence — Débat — Dédicace')
const typeInput = Selector('#offer-type')
const venueAnchor = Selector("a[href^='/structures/']").withText(
  'THEATRE NATIONAL DE CHAILLOT'
)

fixture`06_01 OfferPage | Naviguer vers creer une offre`

test("Lorsque je clique sur le bouton créer une offre sur la page des offres, j'accède au formulaire de création d'offre", async t => {
  await t.useRole(regularOfferer).click(createOfferAnchor)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre sur la page d'un lieu, j'accède au formulaire de création d'offre, et je peux revenir avec le bouton annuler", async t => {
  await t
    .useRole(regularOfferer)
    .click(navbarAnchor)
    .click(offerersNavbarLink)
    .click(offererAnchor)

    .click(venueAnchor)

  await t.click(createOfferFromVenueAnchor)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test('Lorsque je clique sur le bouton annuler une offre sur la page des offres, je reviens aux offres', async t => {
  await t.useRole(regularOfferer).click(createOfferAnchor)

  await t.click(cancelAnchor)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})

fixture`06_02 OfferPage | Créer une nouvelle offre`

test('Je peux créer une offre', async t => {
  await t.useRole(regularOfferer).click(createOfferAnchor)

  await t.typeText(nameInput, 'Rencontre avec Franck Lepage')

  await t.click(typeInput).click(typeOption)

  await t.click(offererInput).click(offererOption)

  await t.typeText(durationMinutesInput, '120')

  await t.typeText(
    descriptionInput,
    [
      'Alors que les licenciements sont devenus des plans de sauvegarde de l’emploi, ',
      'ou que votre banquier se veut votre partenaire, ',
      'il est temps de se poser certaines questions. ',
      'Avec d’autres travailleurs socioculturels, ',
      'lassés des euphémismes et des mensonges du langage du pouvoir, ',
      'Franck Lepage s’est lancé dans cette bataille très politique : celle des mots. ',
      "Atelier d'initiation pour reconnaître tout ce qui est du pipotron dans vos lectures de tous les jours. ",
      "Suivi d'une séance de dédicaces.",
    ].join('')
  )

  await t.click(submitButton)

  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')

  // ADD AN EVENT OCCURENCE AND A STOCK
  await t.click(addScheduleAnchor)

  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  await t.click(scheduleSubmitButton)

  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  await t.typeText(priceInput, '10').typeText(availableInput, '50')

  await t.click(scheduleSubmitButton)

  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion')

  // ADD AN OTHER EVENT OCCURENCE AND A STOCK
  await t.click(addScheduleAnchor)

  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  await t.click(scheduleSubmitButton)

  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  // EDIT ONE
  /*
  await t.click(editScheduleAnchor)

  location = await t.eval(() => window.location)
  await t.expect(location.search)
         .match(/\?gestion&date=([A-Z0-9]*)$/)

  await t.click(scheduleSubmitButton)


  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=([A-Z0-9]*)$/)

  await t.typeText(availableInput, '10')


  await t.click(scheduleSubmitButton)


  location = await t.eval(() => window.location)
  await t.expect(location.search)
         .eql('?gestion')

  // CLOSE
  await t.click(scheduleCloseButton)

  location = await t.eval(() => window.location)
  await t.expect(location.search)
         .eql('')
  */
})
