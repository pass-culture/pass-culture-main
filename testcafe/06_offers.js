import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewOfferAs, navigateToOfferAs, navigateToOffersAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'

const closeInput = Selector('button').withText('Fermer')
const nameInput = Selector('#offer-name')
const offererInput = Selector('#offer-offererId')
const offererOption = Selector('#offer-offererId option')
const typeInput = Selector('#offer-type')
const venueInput = Selector('#offer-venueId')
const venueOption = Selector('#offer-venueId option')
const typeOption = Selector('#offer-type option')
const durationMinutesInput = Selector('input.field-duration')
const descriptionInput = Selector('#offer-description')
const submitButton = Selector('button').withText('Enregistrer')

fixture('En étant sur la page des offres')

test("J'ai accès à l'ensemble de mes offres", async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )
  await navigateToOffersAs(user)(t)

  // when
  const offerItem = Selector('li.offer-item')

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(offerItem.count).gt(0)
})

test('Je recherche une offre et je clique sur celle-ci pour accéder au détail', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )

  // when
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/offres\/([A-Z0-9]*)/)
})

test('Je peux créer une offre de type événement', async t => {
  // given
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
  const eventDuration = '02:00'
  const eventName = 'Rencontre avec Franck Lepage'
  const eventType = 'Conférences, rencontres et découverte des métiers'
  const { name: offererName } = offerer
  const { name: venueName } = venue
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  // when
  await t
    .typeText(nameInput, eventName)
    .click(typeInput)
    .click(typeOption.withText(eventType))
    .click(offererInput)
    .click(offererOption.withText(offererName))
    .click(venueInput)
    .click(venueOption.withText(venueName))
    .typeText(durationMinutesInput, eventDuration)
    .typeText(descriptionInput, eventDescription)
    .click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
})

test('Je peux créer une offre avec des sous-types', async t => {
  // given
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const musicTypeInput = Selector('#offer-musicType')
  const musicTypeOption = Selector('#offer-musicType option')
  const musicSubTypeInput = Selector('#offer-musicSubType')
  const musicSubTypeOption = Selector('#offer-musicSubType option')
  const eventDescription = 'Venez re découvrir PNL en accoustique, sans auto-tune'
  const eventDurationMinutes = '01:30'
  const eventName = 'Concert de PNL Unplugged'
  const eventType = 'Musique - concerts, festivals'
  const eventMusicType = 'Hip-Hop/Rap'
  const eventMusicSubType = 'Rap Alternatif'
  const { name: offererName } = offerer
  const { name: venueName } = venue
  await navigateToNewOfferAs(user)(t)

  // when
  await t
    .typeText(nameInput, eventName)
    .click(typeInput)
    .click(typeOption.withText(eventType))
    .click(musicTypeInput)
    .click(musicTypeOption.withText(eventMusicType))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText(eventMusicSubType))
    .click(offererInput)
    .click(offererOption.withText(offererName))
    .click(venueInput)
    .click(venueOption.withText(venueName))
    .typeText(durationMinutesInput, eventDurationMinutes)
    .typeText(descriptionInput, eventDescription)
    .click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(location.search)
    .eql('?gestion')
    .click(closeInput)
    .expect(musicTypeOption.withText(eventMusicType).exists)
    .ok()
    .expect(musicTypeOption.withText(eventMusicType).selected)
    .ok()
    .expect(musicSubTypeOption.withText(eventMusicSubType).selected)
    .ok()
})
