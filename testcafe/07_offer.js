import { Selector } from 'testcafe'

import {
  navigateToNewOfferAs,
  navigateToOfferAs,
  navigateToVenueAs,
} from './helpers/navigations'
import {
  EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  FUTURE_EVENT_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  FUTURE_MUSIC_EVENT_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  FUTURE_VIRTUAL_THING_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  THING_OFFER_WITH_STOCK_WITH_MEDIATION_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
} from './helpers/offers'
import { OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN } from './helpers/offerers'
import { VALIDATED_UNREGISTERED_OFFERER_USER } from './helpers/users'
import { PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN } from './helpers/venues'

fixture(`OfferPage A | Naviguer vers creer une offre et revenir au précédent`)

test("Lorsque je clique sur le bouton créer une offre sur la page des offres, j'accède au formulaire de création d'offre", async t => {
  // given
  await navigateToNewOfferAs(VALIDATED_UNREGISTERED_OFFERER_USER)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre d'un item structure dans la page structures, j'accède au formulaire de création d'offre", async t => {
  // given
  await navigateToNewOfferAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN
  )(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre d'un item lieu dans la page d'une structure, j'accède au formulaire de création d'offre", async t => {
  // when
  await navigateToNewOfferAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN,
    PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN
  )(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test("Lorsque je clique sur le bouton créer une offre sur la page d'un lieu, j'accède au formulaire de création d'offre", async t => {
  // given
  const newOfferAnchor = Selector("a[href^='/offres/nouveau?lieu=']")
  await navigateToVenueAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN,
    PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN
  )(t)

  // when
  await t.click(newOfferAnchor)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres/nouveau')
})

test('Lorsque je clique sur le bouton annuler une offre sur la page des offres, je reviens aux offres', async t => {
  // given
  const cancelAnchor = Selector('button.button').withText('Annuler')
  await navigateToNewOfferAs(VALIDATED_UNREGISTERED_OFFERER_USER)(t)

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
fixture`OfferPage B | Créer une nouvelle offre`

test('Je peux créer une offre événement', async t => {
  // given
  await navigateToNewOfferAs(VALIDATED_UNREGISTERED_OFFERER_USER)(t)
  const {
    eventDescription,
    eventDurationMinutes,
    eventName,
    eventType,
  } = FUTURE_EVENT_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  const { name: offererName } = OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN
  const {
    name: venueName,
  } = PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN

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
  await navigateToNewOfferAs(VALIDATED_UNREGISTERED_OFFERER_USER)(t)
  const {
    thingDescription,
    thingName,
    thingType,
    thingUrl,
  } = FUTURE_VIRTUAL_THING_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  const { name: offererName } = OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN
  const {
    name: venueName,
  } = PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN

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

test(`Créer des offres avec des sous-types`, async t => {
  // given
  const musicTypeInput = Selector('#offer-musicType')
  const musicTypeOption = Selector('#offer-musicType option')
  const musicSubTypeInput = Selector('#offer-musicSubType')
  const musicSubTypeOption = Selector('#offer-musicSubType option')
  await navigateToNewOfferAs(VALIDATED_UNREGISTERED_OFFERER_USER)(t)
  const {
    eventDescription,
    eventDurationMinutes,
    eventMusicType,
    eventMusicSubType,
    eventName,
    eventType,
  } = FUTURE_MUSIC_EVENT_OFFER_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  const { name: offererName } = OFFERER_WITH_PHYSICAL_VENUE_WITH_IBAN
  const {
    name: venueName,
  } = PHYSICAL_VENUE_WITH_SIRET_WITH_OFFERER_IBAN_WITH_NO_IBAN

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

fixture`OfferPage B | Modifier nouvelle offre`

test("Je vois les détails d'une offre d'object avec 1 stock", async t => {
  // given
  const infoForManagerSpan = Selector('span.nb-dates')

  // when
  await navigateToOfferAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    THING_OFFER_WITH_STOCK_WITH_MEDIATION_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // then
  await t.expect(infoForManagerSpan.innerText).eql('1 stock')
})

test.skip('*TODO* Je peux modifier un événement', async t => {
  // given
  await navigateToOfferAs(
    VALIDATED_UNREGISTERED_OFFERER_USER,
    EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)
})
