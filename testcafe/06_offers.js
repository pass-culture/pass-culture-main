import { Selector } from 'testcafe'

import { isElementInViewport } from './helpers/custom_assertions'
import { getPathname } from './helpers/location'
import { navigateToNewOfferAs, navigateToOfferAs, navigateToOffersAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const offerDetailsTab = Selector('a').withText("Détail de l'offre")
const nameInput = Selector('.offer-form [name="name"]')
const offererInput = Selector('.offer-form [name="offererId"]')
const offererOption = Selector('.offer-form [name="offererId"] option')
const typeInput = Selector('.offer-form [name="type"]')
const venueInput = Selector('.offer-form [name="venueId"]')
const venueOption = Selector('.offer-form [name="venueId"] option')
const typeOption = Selector('.offer-form [name="type"] option')
const durationMinutesInput = Selector('.offer-form [name="durationMinutes"]')
const descriptionInput = Selector('.offer-form [name="description"]')
const isDuo = Selector('.offer-form [name="isDuo"]')
const noDisabilityCompliantCheckbox = '.offer-form [name="noDisabilityCompliant"]'
const thumbnailButton = Selector('.of-placeholder')
const importFromUrlButton = Selector('.thumbnail-dialog .bc-step:not(.active) a')
const importFromUrlInput = Selector('.thumbnail-dialog .tnf-form input[name="url"]')
const importFromUrlSubmitButton = Selector('.thumbnail-dialog .tnf-url-button')
const creditSubmitButton = Selector('.thumbnail-dialog .tnd-actions .primary-button')
const previewSubmitButton = Selector('.thumbnail-dialog .tnd-actions .primary-button')
const validateThumbnailButton = Selector('.thumbnail-dialog .tnd-actions .primary-button')
const submitButton = Selector('.actions-section .primary-button')

fixture('En étant sur la page des offres,')

test('j’ai accès à l’ensemble de mes offres', async t => {
  const { user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )
  const offerItem = Selector('.offer-item')
  await navigateToOffersAs(user)(t)

  await t.expect(getPathname()).eql('/offres').expect(offerItem.count).gt(0)
})

test('je recherche une offre et je clique sur celle-ci pour accéder au détail', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  await t.expect(getPathname()).match(/\/offres\/([A-Z0-9]*)/)
})

test('je peux créer une offre de type événement', async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const userRole = createUserRole(user)
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

  await navigateToNewOfferAs(user, offerer, venue, userRole)(t)

  await t
    .click(typeInput)
    .click(typeOption.withText('Conférences, rencontres et découverte des métiers'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(noDisabilityCompliantCheckbox)
    .typeText(durationMinutesInput, '02:00')
    .typeText(descriptionInput, eventDescription)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offres\/([A-Z0-9]+)\/stocks$/)
})

test('je peux créer une offre avec des sous-types', async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const musicTypeInput = Selector('.offer-form [name="musicType"]')
  const musicTypeOption = Selector('.offer-form [name="musicType"] option')
  const musicSubTypeInput = Selector('.offer-form [name="musicSubType"]')
  const musicSubTypeOption = Selector('.offer-form [name="musicSubType"] option')
  const eventMusicType = 'Hip-Hop/Rap'
  const eventMusicSubType = 'Rap Alternatif'
  await navigateToNewOfferAs(user, offerer, venue)(t)

  await t
    .click(typeInput)
    .click(typeOption.withText('Musique - concerts, festivals'))
    .typeText(nameInput, 'Concert de PNL Unplugged')
    .click(musicTypeInput)
    .click(musicTypeOption.withText(eventMusicType))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText(eventMusicSubType))
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(noDisabilityCompliantCheckbox)
    .typeText(durationMinutesInput, '01:30')
    .typeText(descriptionInput, 'Venez re découvrir PNL en accoustique, sans auto-tune')
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offres\/([A-Z0-9]+)\/stocks$/)
    .click(offerDetailsTab)
    .expect(musicTypeOption.withText(eventMusicType).exists)
    .ok()
    .expect(musicTypeOption.withText(eventMusicType).selected)
    .ok()
    .expect(musicSubTypeOption.withText(eventMusicSubType).selected)
    .ok()
})

test('une offre Event est duo par défaut', async t => {
  const { user, offerer, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  await navigateToNewOfferAs(user, offerer, venue)(t)

  await t
    .click(typeInput)
    .click(typeOption.withText('Spectacle vivant')) // choose an event
    .typeText(nameInput, 'Offre Duo')
    .expect(isDuo.checked)
    .ok()
    .click(isDuo)
    .expect(isDuo.checked) // Make sure we can uncheck
    .notOk()
    .click(isDuo)
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .click(offerDetailsTab)
    .expect(isDuo.checked)
    .ok()
    .expect(isDuo.checked)
    .ok()
    .click(isDuo) // Uncheck isDuo
    .click(submitButton)
    .expect(isDuo.checked)
    .notOk()
})

test("je peux modifier la thumbnail d'une offre", async t => {
  const offerThumbnail = Selector('.of-image img')
  const { offer, user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_offer_with_at_least_one_thumbnail'
  )
  await navigateToOfferAs(user, offer)(t)

  const previousThumbnailSrc = await offerThumbnail().attributes['src']
  await t
    .click(thumbnailButton)
    .click(importFromUrlButton)
    .typeText(
      importFromUrlInput,
      'https://upload.wikimedia.org/wikipedia/commons/f/f9/Zebra_%28PSF%29.png'
    )
    .click(importFromUrlSubmitButton)
    .click(creditSubmitButton)
    .click(previewSubmitButton)
    .click(validateThumbnailButton)
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
  await t.eval(() => location.reload(true))
  const updatedThumbnail = await offerThumbnail()
  await t.expect(updatedThumbnail.attributes['src'] === previousThumbnailSrc).notOk()
})

test("Je suis scrollé sur l'élément incorrect du formulaire d'édition d'offre", async t => {
  const { offer, user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_offer_with_at_least_one_thumbnail'
  )
  await navigateToOfferAs(user, offer, createUserRole(user))(t)
  const key_combination_to_delete_text_input = 'ctrl+a delete'

  await t
    .click(nameInput())
    .pressKey(key_combination_to_delete_text_input)
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(isElementInViewport('.offer-form [name="name"]'))
    .ok({ timeout: 2000 })
})
