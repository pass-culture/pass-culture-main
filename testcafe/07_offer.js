import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateToNewOfferAs,
  navigateToOfferAs,
  navigateToVenueAs,
} from './helpers/navigations'
import { createUserRole } from './helpers/roles'

const closeInput = Selector('button').withText('Fermer')
const nameInput = Selector('#offer-name')
const offererInput = Selector('#offer-offererId')
const offererOption = Selector('#offer-offererId option')
const typeInput = Selector('#offer-type')
const urlInput = Selector('#offer-url')
const venueInput = Selector('#offer-venueId')
const venueOption = Selector('#offer-venueId option')
const typeOption = Selector('#offer-type option')
const durationMinutesInput = Selector('#offer-durationMinutes')
const descriptionInput = Selector('#offer-description')
const submitButton = Selector('button.button.is-primary').withText(
  'Enregistrer'
)

fixture('Initialisation')

let userRoleOne
let userRoleTwo
let userRoleThree
let userRoleFour
let userRoleFive
let dataFromSandboxOne
let dataFromSandboxTwo
let dataFromSandboxThree
let dataFromSandboxFour
let dataFromSandboxFive
test('Création des données', async () => {
  dataFromSandboxOne = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer'
  )
  userRoleOne = createUserRole(dataFromSandboxOne.user)

  dataFromSandboxTwo = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  userRoleTwo = createUserRole(dataFromSandboxTwo.user)

  dataFromSandboxThree = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_virtual_venue'
  )
  userRoleThree = createUserRole(dataFromSandboxThree.user)

  dataFromSandboxFour = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_thing_offer_with_one_stock'
  )
  userRoleFour = createUserRole(dataFromSandboxFour.user)

  dataFromSandboxFive = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_event_offer'
  )
  userRoleFive = createUserRole(dataFromSandboxFive.user)
})

fixture('Offer A | Naviguer vers "Créer une offre" et revenir au précédent')

test("Lorsque je clique sur le bouton 'créer une offre' sur la page des offres, j'accède au formulaire de création d'offre", async t => {
  // given
  const { user } = dataFromSandboxOne
  await navigateToNewOfferAs(user, null, null, userRoleOne)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/creation')
})

test("Lorsque je clique sur le bouton 'créer une offre' d'un item structure dans la page structures, j'accède au formulaire de création d'offre", async t => {
  // given
  const { offerer, user } = dataFromSandboxTwo
  await navigateToNewOfferAs(user, offerer, null, userRoleTwo)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/creation')
})

test("Lorsque je clique sur le bouton 'créer une offre' d'un item lieu dans la page d'une structure, j'accède au formulaire de création d'offre", async t => {
  // when
  const { offerer, user, venue } = dataFromSandboxTwo
  await navigateToNewOfferAs(user, offerer, venue, userRoleTwo)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/creation')
})

test("Lorsque je clique sur le bouton 'créer une offre' sur la page d'un lieu, j'accède au formulaire de création d'offre", async t => {
  // given
  const { offerer, user, venue } = dataFromSandboxTwo
  const newOfferAnchor = Selector("a[href^='/offres/creation?lieu=']")
  await navigateToVenueAs(user, offerer, venue, userRoleTwo)(t)

  // when
  await t.click(newOfferAnchor)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/creation')
})

test("Lorsque je clique sur le bouton 'annuler' de la page 'créer une offre' sur la page des offres, je reviens au mode read-only de l'offre", async t => {
  // given
  const { user } = dataFromSandboxOne
  const cancelButton = Selector('#cancel-button').withText('Annuler')
  await navigateToNewOfferAs(user, null, null, userRoleOne)(t)

  // when
  await t.click(cancelButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})

fixture('Offer B | Créer une nouvelle offre')

test('Je peux créer une offre événement', async t => {
  // given
  const { offerer, user, venue } = dataFromSandboxTwo
  await navigateToNewOfferAs(user, null, null, userRoleTwo)(t)
  const eventDescription = [
    'Alors que les licenciements sont devenus des plans de sauvegarde de l’emploi, ',
    'ou que votre banquier se veut votre partenaire, ',
    'il est temps de se poser certaines questions. ',
    'Avec d’autres travailleurs socioculturels, ',
    'lassés des euphémismes et des mensonges du langage du pouvoir, ',
    'Franck Lepage s’est lancé dans cette bataille très politique : celle des mots. ',
    "Atelier d'initiation pour reconnaître tout ce qui est du pipotron dans vos lectures de tous les jours. ",
    "Suivi d'une séance de dédicaces.",
  ].join('')
  const eventDurationMinutes = '120'
  const eventName = 'Rencontre avec Franck Lepage'
  const eventType = 'Conférences, rencontres et découverte des métiers'
  const { name: offererName } = offerer
  const { name: venueName } = venue

  // when
  await t.typeText(nameInput, eventName)
  await t.click(typeInput).click(typeOption.withText(eventType))
  await t.click(offererInput).click(offererOption.withText(offererName))
  await t.click(venueInput).click(venueOption.withText(venueName))
  await t.typeText(durationMinutesInput, eventDurationMinutes)
  await t.typeText(descriptionInput, eventDescription)
  await t.click(submitButton)

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
})

test('Je peux créer une offre numérique', async t => {
  // given
  const { offerer, user, venue } = dataFromSandboxThree
  await navigateToNewOfferAs(user, null, null, userRoleThree)(t)
  const { name: offererName } = offerer
  const { name: venueName } = venue

  // when
  await t.typeText(nameInput, 'Jeux vidéo abonnement de test')
  await t.click(typeInput).click(typeOption.withText('Jeux vidéo'))
  await t.click(offererInput).click(offererOption.withText(offererName))
  await t.click(venueInput).click(venueOption.withText(venueName))
  await t.typeText(urlInput, 'http://www.example.com')
  await t.typeText(descriptionInput, 'Jeux vidéo de test')
  await t.click(submitButton)

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
})

test('Je peux créer des offres avec des sous-types', async t => {
  // given
  const { offerer, user, venue } = dataFromSandboxTwo
  const musicTypeInput = Selector('#offer-musicType')
  const musicTypeOption = Selector('#offer-musicType option')
  const musicSubTypeInput = Selector('#offer-musicSubType')
  const musicSubTypeOption = Selector('#offer-musicSubType option')
  const eventDescription =
    'Venez re découvrir PNL en accoustique, sans auto-tune'
  const eventDurationMinutes = '90'
  const eventName = 'Concert de PNL Unplugged'
  const eventType = 'Musique — concerts, festivals'
  const eventMusicType = 'Hip-Hop/Rap'
  const eventMusicSubType = 'Rap Alternatif'
  const { name: offererName } = offerer
  const { name: venueName } = venue
  await navigateToNewOfferAs(user)(t)

  // when
  await t.typeText(nameInput, eventName)
  await t.click(typeInput).click(typeOption.withText(eventType))
  await t.click(musicTypeInput).click(musicTypeOption.withText(eventMusicType))
  await t
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText(eventMusicSubType))
  await t.click(offererInput).click(offererOption.withText(offererName))
  await t.click(venueInput).click(venueOption.withText(venueName))
  await t.typeText(durationMinutesInput, eventDurationMinutes)
  await t.typeText(descriptionInput, eventDescription)
  await t.click(submitButton)

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
    .click(closeInput)

  await t
    .expect(musicTypeOption.withText(eventMusicType).exists)
    .ok()
    .expect(musicTypeOption.withText(eventMusicType).selected)
    .ok()
    .expect(musicSubTypeOption.withText(eventMusicSubType).selected)
    .ok()
})

fixture.skip('*TODO* Offer B | Modifier nouvelle offre')

test('Je peux modifier un objet', async t => {
  // given
  const { offer, user } = dataFromSandboxFour
  await navigateToOfferAs(user, offer, userRoleFour)(t)
})

test('Je peux modifier un événement', async t => {
  // given
  const { offer, user } = dataFromSandboxFive
  await navigateToOfferAs(user, offer, userRoleFive)(t)
})
