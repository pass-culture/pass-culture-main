import { getPathname, goBack } from './helpers/location'
import {
  navigateToNewOfferAs,
  navigateToOfferAs,
  navigateToOffersAs,
} from './helpers/navigations'

/* eslint-disable max-lines */
import { Selector } from 'testcafe'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { isElementInViewport } from './helpers/custom_assertions'

const nameInput = Selector('.offer-form [name="name"]')
const offererInput = Selector('.offer-form [name="offererId"]')
const offererOption = Selector('.offer-form [name="offererId"] option')
const categoryInput = Selector('.offer-form [name="categoryId"]')
const subcategoryInput = Selector('.offer-form [name="subcategoryId"]')
const subcategoryOption = Selector('.offer-form [name="subcategoryId"] option')
const showTypeInput = Selector('.offer-form [name="showType"]')
const showTypeOption = Selector('.offer-form [name="showType"] option')
const venueInput = Selector('.offer-form [name="venueId"]')
const venueOption = Selector('.offer-form [name="venueId"] option')
const categoryOption = Selector('.offer-form [name="categoryId"] option')
const withdrawalType = Selector('.input-radio-input[name="withdrawalType"]')
const durationMinutesInput = Selector('.offer-form [name="durationMinutes"]')
const descriptionInput = Selector('.offer-form [name="description"]')
const isDuo = Selector('.offer-form [name="offerOption"]').withAttribute(
  'value',
  'DUO'
)
const isNotDuo = Selector('.offer-form [name="offerOption"]').withAttribute(
  'value',
  'NONE'
)
const noDisabilityCompliantCheckbox =
  '.offer-form [name="noDisabilityCompliant"]'
const thumbnailButton = Selector('.of-placeholder')
const submitButton = Selector('.actions-section .primary-button')
const navBrandLogoItem = Selector('.nav-brand .logo')
const exitOfferCreationMessage = Selector('h3').withText(
  'Voulez-vous quitter la création d’offre ?'
)
const exitOfferCreationDialogConfirmButton =
  Selector('button').withExactText('Quitter')
const exitOfferCreationDialogCancelButton =
  Selector('button').withExactText('Annuler')

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

  await t.expect(getPathname()).match(/\/offre\/([A-Z0-9]*)/)
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
    .click(categoryInput)
    .click(categoryOption.withText('Conférences, rencontres'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Conférence'))
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
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
})

test('je peux créer une offre avec des sous-types', async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const musicTypeInput = Selector('.offer-form [name="musicType"]')
  const musicTypeOption = Selector('.offer-form [name="musicType"] option')
  const musicSubTypeInput = Selector('.offer-form [name="musicSubType"]')
  const musicSubTypeOption = Selector(
    '.offer-form [name="musicSubType"] option'
  )
  const eventMusicType = 'Hip-Hop/Rap'
  const eventMusicSubType = 'Rap Alternatif'
  await navigateToNewOfferAs(user, offerer, venue)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Musique live'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Concert'))
    .typeText(nameInput, 'Concert de PNL Unplugged')
    .click(musicTypeInput)
    .click(musicTypeOption.withText(eventMusicType))
    .click(musicSubTypeInput)
    .click(musicSubTypeOption.withText(eventMusicSubType))
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(withdrawalType)
    .click(noDisabilityCompliantCheckbox)
    .typeText(durationMinutesInput, '01:30')
    .typeText(
      descriptionInput,
      'Venez re découvrir PNL en accoustique, sans auto-tune'
    )
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
})

test('une offre Event est duo par défaut', async t => {
  const { user, offerer, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  await navigateToNewOfferAs(user, offerer, venue)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Spectacle vivant')) // choose an event
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Festival'))
    .click(showTypeInput)
    .click(showTypeOption.withText('Cirque'))
    .typeText(nameInput, 'Offre Duo')
    .expect(isDuo.checked)
    .ok()
    .click(isNotDuo)
    .expect(isDuo.checked) // Make sure we can uncheck
    .notOk()
    .click(isDuo)
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(withdrawalType)
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
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
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
  await t.eval(() => location.reload(true))
  const updatedThumbnail = await offerThumbnail()
  await t
    .expect(updatedThumbnail.attributes['src'] === previousThumbnailSrc)
    .notOk()
})

test("je suis scrollé sur l'élément incorrect du formulaire d'édition d'offre", async t => {
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

// skip this test until flakiness is fixed
test.skip("je suis empêché de quitter la création d'offre sans confirmation", async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(noDisabilityCompliantCheckbox)
    .click(navBrandLogoItem)
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogCancelButton)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
    .click(navBrandLogoItem())
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogCancelButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
})

test("je peux quitter la création d'offre avec confirmation", async t => {
  const { offerer, user, venue } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(offererInput)
    .click(offererOption.withText(offerer.name))
    .click(venueInput)
    .click(venueOption.withText(venue.name))
    .click(noDisabilityCompliantCheckbox)
    .click(navBrandLogoItem)
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogConfirmButton)
    .expect(getPathname())
    .match(/\/accueil$/)
})

test('je peux créer une offre avec médiation', async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(thumbnailButton)
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)
})

test("je suis redirigé sur la page de choix du type d'offre si je clique sur retour à partir de la page de création d'offre", async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')

  await goBack()

  await t
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogConfirmButton)
    .expect(getPathname())
    .eql('/offre/creation')
})

// skip this test until flakiness is fixed
test.skip("je suis redirigé sur la liste des offres si je clique sur retour à partir de la page des stock au moment de la création d'offre", async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)

  await goBack()

  await t
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogConfirmButton)
    .expect(getPathname())
    .eql('/offres')
})

test("je suis redirigé sur la liste des offres si je clique sur retour à partir de la page de confirmation de la création d'offre", async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)

  const addThingStockButton = Selector('button').withText('Ajouter un stock')
  const priceInput = Selector('input[name="price"]')
  const validateAndCreateOffer = Selector('button').withText(
    'Valider et créer l’offre'
  )

  await t
    .click(addThingStockButton)
    .typeText(priceInput, '15')
    .click(validateAndCreateOffer)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/confirmation$/)

  await goBack()

  await t.expect(getPathname()).eql('/offres')
})

// skip this test until flakiness is fixed
test.skip('je suis redirigé sur la liste des offres si je clique sur retour à partir de la page de création quand je viens de la confirmation', async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  const userRole = createUserRole(user)
  await navigateToNewOfferAs(user, null, null, userRole)(t)

  await t
    .click(categoryInput)
    .click(categoryOption.withText('Films, vidéos'))
    .click(subcategoryInput)
    .click(subcategoryOption.withText('Support physique (DVD, Blu-ray...)'))
    .typeText(nameInput, 'Rencontre avec Franck Lepage')
    .click(noDisabilityCompliantCheckbox)
    .click(submitButton)
    .expect(getPathname())
    .match(/\/offre\/([A-Z0-9]+)\/individuel\/stocks$/)

  const addThingStockButton = Selector('button').withText('Ajouter un stock')
  const priceInput = Selector('input[name="price"]')
  const validateAndCreateOffer = Selector('button').withText(
    'Valider et créer l’offre'
  )
  const createANewOffer = Selector('a').withText('Créer une nouvelle offre')

  await t
    .click(addThingStockButton)
    .typeText(priceInput, '15')
    .click(validateAndCreateOffer)
    .click(createANewOffer)
    .expect(getPathname())
    .match(/\/offre\/creation\/individuel$/)

  await goBack()

  await t
    .expect(exitOfferCreationMessage.exists)
    .ok()
    .click(exitOfferCreationDialogConfirmButton)

  await t.expect(getPathname()).eql('/offres')
})
