// $(yarn bin)/testcafe chrome ./testcafe/04_04_verso_with_share.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const discoverURL = `${ROOT_PATH}decouverte`

const dragButton = Selector('#dragButton')
const openVersoButton = Selector('#deck-open-verso-button')

const versoOfferLabel = Selector('#verso-offer-label')
const versoOfferName = Selector('#verso-offer-name')
const versoOfferVenue = Selector('#verso-offer-venue')
const versoOfferWhen = Selector('#verso-offer-when')
const versoOfferAdress = Selector('#verso-offer-adress')
const versoOfferDescription = Selector('#verso-offer-description')
const versoOfferAuthor = Selector('#verso-offer-author')
const versoOfferPerformer = Selector('#verso-offer-performer')
const versoOfferSpeaker = Selector('#verso-offer-speaker')
const versoOfferDirector = Selector('#verso-offer-director')
const versoOfferDuration = Selector('#verso-offer-duration')
const versoOfferLimitDateTime = Selector('#verso-offer-limit-date-time')
const versoOfferPostalCode = Selector('#verso-offer-postal-code')
const versoOfferCity = Selector('#verso-offer-city')
const versoOfferDistance = Selector('#verso-offer-distance')
const versoOfferType = Selector('#verso-offer-type')
const versoOfferHasMoreBookables = Selector('#verso-offer-has-more-bookables')
const versoOfferReserved = Selector('#verso-offer-reserved')

fixture(`04_05 Verso détails de l'offre`)

test('Le titre et le nom du lieu sont affichés', async t => {
  // given
  const { user, recommendation } = await fetchSandbox(
    'webapp_03_decouverte',
    'get_existing_webapp_user_with_at_least_one_recommendation'
  )

  const offerURL = `${discoverURL}/${recommendation.offerId}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
  const offerTitle = recommendation.offer.name
  const offerVenue = recommendation.offer.venue.name
  const offerDescription = recommendation.offer.description
  const offerDate = 'Dès maintenant '
  const offerType = recommendation.offer.product.offerType.appLabel

  const offerVenueAdress = recommendation.offer.venue.address
  const offerVenueCity = recommendation.offer.venue.city
  const offerVenuePostalCode = recommendation.offer.venue.postalCode

  await t
    .click(openVersoButton)

    // Header Title
    .expect(versoOfferName.textContent)
    .contains(offerTitle)
    .expect(versoOfferVenue.textContent)
    .eql(offerVenue)

    // Détails
    .expect(versoOfferDescription.textContent)
    .eql(offerDescription)

    // Quoi ?
    .expect(versoOfferAuthor.exists)
    .notOk()
    .expect(versoOfferDuration.exists)
    .notOk()
    .expect(versoOfferPerformer.exists)
    .notOk()
    .expect(versoOfferType.exists)
    .notOk()
    .expect(versoOfferLabel.textContent)
    .eql(offerType)
    .expect(versoOfferSpeaker.exists)
    .notOk()
    .expect(versoOfferDirector.exists)
    .notOk()

    // Quand ?
    .expect(versoOfferWhen.textContent)
    .eql('Dès maintenant ')

    // Thing Date
    .expect(versoOfferLimitDateTime.textContent)
    .eql(offerDate)

    // Event Date
    .expect(versoOfferHasMoreBookables.exists)
    .notOk()
    .expect(versoOfferReserved.exists)
    .notOk()

    // Où ?
    .expect(versoOfferAdress.textContent)
    .eql(offerVenueAdress)
    .expect(versoOfferCity.textContent)
    .eql(offerVenueCity)
    .expect(versoOfferDistance.exists)
    .ok()
    .expect(versoOfferPostalCode.textContent)
    .eql(offerVenuePostalCode)
})
