import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateToNewOfferAs,
  navigateToOfferAs,
  navigateToVenueAs,
} from './helpers/navigations'

fixture('Offer A | Naviguer vers creer une offre et revenir au précédent')

test("Lorsque je clique sur le bouton créer une offre sur la page des offres, j'accède au formulaire de création d'offre", async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer'
  )
  await navigateToNewOfferAs(user)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre d'un item structure dans la page structures, j'accède au formulaire de création d'offre", async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  await navigateToNewOfferAs(user, offerer)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre d'un item lieu dans la page d'une structure, j'accède au formulaire de création d'offre", async t => {
  // when
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  await navigateToNewOfferAs(user, offerer, venue)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre sur la page d'un lieu, j'accède au formulaire de création d'offre", async t => {
  // given
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const newOfferAnchor = Selector("a[href^='/offres/nouveau?lieu=']")
  await navigateToVenueAs(user, offerer, venue)(t)

  // when
  await t.click(newOfferAnchor)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test('Lorsque je clique sur le bouton annuler une offre sur la page des offres, je reviens aux offres', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_at_least_one_visible_offer'
  )
  const cancelAnchor = Selector('button.button').withText('Annuler')
  await navigateToNewOfferAs(user)(t)

  // when
  await t.click(cancelAnchor)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})

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
fixture('Offer B | Créer une nouvelle offre')

test('Je peux créer une offre événement', async t => {
  // given
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  await navigateToNewOfferAs(user)(t)
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
  const eventType = 'Conférence — Débat — Dédicace'
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
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_virtual_venue'
  )
  await navigateToNewOfferAs(user)(t)
  const thingDescription = 'Jeux vidéo de test'
  const thingName = 'Jeux vidéo abonnement de test'
  const thingType = 'Jeux Vidéo'
  const thingUrl = 'http://www.example.com'
  const { name: offererName } = offerer
  const { name: venueName } = venue

  // when
  await t.typeText(nameInput, thingName)
  await t.click(typeInput).click(typeOption.withText(thingType))
  await t.click(offererInput).click(offererOption.withText(offererName))
  await t.click(venueInput).click(venueOption.withText(venueName))
  await t.typeText(urlInput, thingUrl)
  await t.typeText(descriptionInput, thingDescription)
  await t.click(submitButton)

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
})

test('Créer des offres avec des sous-types', async t => {
  // given
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const musicTypeInput = Selector('#offer-musicType')
  const musicTypeOption = Selector('#offer-musicType option')
  const musicSubTypeInput = Selector('#offer-musicSubType')
  const musicSubTypeOption = Selector('#offer-musicSubType option')
  const eventDescription =
    'Venez re découvrir PNL en accoustique, sans auto-tune'
  const eventDurationMinutes = '90'
  const eventName = 'Concert de PNL Unplugged'
  const eventType = 'Musique (Concerts, Festivals)'
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
  const { offer, user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_thing_offer_with_one_stock'
  )
  await navigateToOfferAs(user, offer)(t)
})

test('Je peux modifier un événement', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_event_offer'
  )
  await navigateToOfferAs(user, offer)(t)
})
