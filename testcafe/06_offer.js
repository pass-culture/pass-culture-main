import { Selector } from 'testcafe'

import { regularOfferer } from './helpers/roles'

const cancelAnchor = Selector('button.button').withText('Annuler')
const createOfferAnchor = Selector("a[href^='/offres/nouveau']")
const createOfferFromVenueAnchor = Selector("a[href^='/offres/nouveau?lieu=']")
const nameInput = Selector('#offer-name')
const navbarAnchor = Selector(
  'a.navbar-link, span.navbar-burger'
).filterVisible()
const offererAnchor = Selector("a[href^='/structures/']").withText(
  'THEATRE NATIONAL DE CHAILLOT'
)
const offererInput = Selector('#offer-offererId')
const offererOption = Selector('option').withText(
  'THEATRE NATIONAL DE CHAILLOT'
)
const offerersNavbarLink = Selector("a.navbar-item[href='/structures']")
const priceInput = Selector('#stock-price')
const stockBookingLimitDatetimeInput = Selector('#stock-bookingLimitDatetime')
const scheduleCloseButton = Selector('button.button').withText('Fermer')
const scheduleSubmitButton = Selector('button.button.submitStep')
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

const typeInput = Selector('#offer-type')
const venueInput = Selector('#offer-venueId')
const venueOption = Selector('#offer-venueId option')
const typeOption = Selector('#offer-type option')
const musicTypeInput = Selector('#offer-musicType')
const musicTypeOption = Selector('#offer-musicType option')
const musicSubTypeInput = Selector('#offer-musicSubType')
const musicSubTypeOption = Selector('#offer-musicSubType option')
const durationMinutesInput = Selector('#offer-durationMinutes')
const descriptionInput = Selector('#offer-description')
const submitButton = Selector('button.button.is-primary').withText(
  'Enregistrer'
)
const addScheduleAnchor = Selector('#add-occurrence-or-stock')

fixture`06_02 OfferPage | Créer une nouvelle offre événement`

test('Je peux créer une offre événement', async t => {
  await t.useRole(regularOfferer).click(createOfferAnchor)
  await t.typeText(nameInput, 'Rencontre avec Franck Lepage')
  await t
    .click(typeInput)
    .click(typeOption.withText('Conférence — Débat — Dédicace'))
    .click(venueInput)
    .click(venueOption.withText('THEATRE NATIONAL DE CHAILLOT'))
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
})

test("Je peux créer une occurence d'événement", async t => {
  await t.useRole(regularOfferer)

  const editOfferAnchor = Selector('a.editLink:first-child')
  const manageStockAnchor = Selector('a.manageStock')

  await t
    .click(editOfferAnchor)
    .click(manageStockAnchor)
    .click(addScheduleAnchor)

  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')
  await t.click(scheduleSubmitButton)
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  const availableInput = Selector('#stock-available')
  await t.typeText(priceInput, '10').typeText(availableInput, '50')
  await t.click(scheduleSubmitButton)
  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion')
})

test('Je peux créer une autre occurence', async t => {
  // ADD AN OTHER EVENT OCCURENCE AND A STOCK
  await t.useRole(regularOfferer)

  const editOfferAnchor = Selector('a.editLink:first-child')
  const manageStockAnchor = Selector('a.manageStock')

  await t
    .click(editOfferAnchor)
    .click(manageStockAnchor)
    .click(addScheduleAnchor)
  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')
  await t.click(scheduleSubmitButton)
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  // EDIT ONE
  /*
  const editScheduleAnchor = Selector(
    "a.button[href^='/offres/A9?gestion&date=']"
  )

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

fixture`06_02 OfferPage | Créer une nouvelle offre avec type et sous-type`

test('Je peux créer une offre avec type et sous-type', async t => {
  await t
    .useRole(regularOfferer)
    .click(createOfferAnchor)
    .typeText(nameInput, 'Concert de PNL Unplugged')
    .click(typeInput)
    .click(typeOption.withText('Musique (Concerts, Festivals)'))
    .click(musicTypeInput)
    .click(musicTypeOption.withText('Hip-Hop/Rap'))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText('Rap Alternatif'))
    .click(venueInput)
    .click(venueOption.withText('THEATRE NATIONAL DE CHAILLOT'))
    .click(offererInput)
    .click(offererOption)
    .typeText(durationMinutesInput, '90')
    .typeText(
      descriptionInput,
      'Venez re découvrir PNL en accoustique, sans auto-tune'
    )
    .click(submitButton)

  let location = await t.eval(() => window.location)

  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')

    .click(closeInput)

    .expect(musicTypeOption.withText('Hip-Hop/Rap').exists)
    .ok()
    .expect(musicTypeOption.withText('Hip-Hop/Rap').selected)
    .ok()
    .expect(musicSubTypeOption.withText('Rap Alternatif').selected)
    .ok()
})

const structuresLink = Selector("a[href='/structures']").withText('Structures')
const createVirtualOfferAnchor = Selector(
  "a[href^='/offres/nouveau']"
).withText('Nouvelle offre numérique')
const typeVideoGameOption = Selector('option').withText('Jeux Vidéo')
const offerUrlInput = Selector('#offer-url')
const closeInput = Selector('button').withText('Fermer')
const offerGoToGestionButton = Selector('.nb-dates')

fixture`06_03 OfferPage | Créer une nouvelle offre numérique`

test('Je peux créer une offre numérique', async t => {
  await t
    .useRole(regularOfferer)
    .wait(500)
    .click(navbarAnchor)
    .click(structuresLink)
    .wait(500)
  await t.click(createVirtualOfferAnchor)
  await t.typeText(nameInput, 'Jeux vidéo abonnement de test')
  await t.click(typeInput).click(typeVideoGameOption)
  await t.typeText(offerUrlInput, 'http://www.example.com')
  await t.typeText(descriptionInput, 'Jeux vidéo de test')
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
  await t.expect(location.search).eql('?gestion&stock=nouveau')
  await t.typeText(priceInput, '20')
  // await t.typeText(stockBookingLimitDatetimeInput, 20)
  await t.click(scheduleSubmitButton)
  location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion$/)

  const offerId = location.pathname.replace('/offres/', '')

  if (await !addScheduleAnchor.exists) {
    t.expect(true).eql(false)
  }

  await t.click(closeInput)
  await t.expect(offerGoToGestionButton.innerText).eql('1 stock')

  // await t.click()

  // Check price quantity on list page
  // TODO Should probably be deported in offers test
  await t.click('a.back-button')
  const listGoToGestionButton = Selector(`a[href="/offres/${offerId}?gestion"]`)
  await t.expect(listGoToGestionButton.innerText).eql('1 prix')
})
