import { Selector } from 'testcafe'

import { getPathname, getUrlParams } from './helpers/location'
import { navigateToNewOfferAs, navigateToOfferAs, navigateToOffersAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

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
const isDuo = Selector('#isDuo')
const submitButton = Selector('button').withText('Enregistrer')

fixture('En étant sur la page des offres,')

test('j’ai accès à l’ensemble de mes offres', async t => {
  const { user } = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )
  const offerItem = Selector('.offer-item')
  await navigateToOffersAs(user)(t)

  await t
    .expect(getPathname())
    .eql('/offres')
    .expect(offerItem.count)
    .gt(0)
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
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(typeInput)
    .click(typeOption.withText('Conférences, rencontres et découverte des métiers'))
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .typeText(durationMinutesInput, '02:00')
    .typeText(descriptionInput, eventDescription)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(getUrlParams())
    .eql('?gestion')
})

test('je peux créer une offre avec des sous-types', async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const musicTypeInput = Selector('#offer-musicType')
  const musicTypeOption = Selector('#offer-musicType option')
  const musicSubTypeInput = Selector('#offer-musicSubType')
  const musicSubTypeOption = Selector('#offer-musicSubType option')
  const eventMusicType = 'Hip-Hop/Rap'
  const eventMusicSubType = 'Rap Alternatif'
  await navigateToNewOfferAs(user)(t)

  await t
    .typeText(nameInput, 'Concert de PNL Unplugged')
    .click(typeInput)
    .click(typeOption.withText('Musique - concerts, festivals'))
    .click(musicTypeInput)
    .click(musicTypeOption.withText(eventMusicType))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText(eventMusicSubType))
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .typeText(durationMinutesInput, '01:30')
    .typeText(descriptionInput, 'Venez re découvrir PNL en accoustique, sans auto-tune')
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offres\/([A-Z0-9]*)$/)
    .expect(getUrlParams())
    .eql('?gestion')
    .click(closeInput)
    .expect(musicTypeOption.withText(eventMusicType).exists)
    .ok()
    .expect(musicTypeOption.withText(eventMusicType).selected)
    .ok()
    .expect(musicSubTypeOption.withText(eventMusicSubType).selected)
    .ok()
})



test('une offre Event est duo par défaut', async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const buttonClose = Selector('#close-manager')
  const buttonModifyOffer = Selector('#modify-offer-button')
  await navigateToNewOfferAs(user)(t)

  await t
    .typeText(nameInput, 'Offre Duo')
    .click(typeInput)
    .click(typeOption.withText('Spectacle vivant')) // choose an event
    // .click(isDuo) // TODO: remove. We shouldn't need this. 
    .expect(isDuo.checked)
    .ok() // First fail: isDuo should be checked by default for events
    .click(isDuo)
    .expect(isDuo.checked) // Make sure we can uncheck
    .notOk()
    .click(isDuo)
    .click(submitButton)
    .click(buttonClose)
    .expect(isDuo.checked)
    .ok()
    .click(buttonModifyOffer)
    .expect(isDuo.checked)
    .ok()
    .click(isDuo) // Uncheck isDuo
    .click(submitButton)
    .expect(isDuo.checked)
    .notOk() // Second fail: TODO: this should be true
})
