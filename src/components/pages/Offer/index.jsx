import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawOffer from './RawOffer'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'
import selectEventById from 'selectors/selectEventById'
import eventOrThingPatchSelector from 'selectors/eventOrThingPatch'
import selectOfferById from 'selectors/selectOfferById'
import selectOffererById from 'selectors/selectOffererById'
import offerersSelector from 'selectors/offerers'
import selectProviders from 'selectors/selectProviders'
import selectMusicSubOptionsByMusicType from 'selectors/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from 'selectors/selectShowSubOptionsByShowType'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import selectThingById from 'selectors/selectThingById'
import typesSelector from 'selectors/types'
import { typeSelector } from 'selectors/type'
import selectVenueById from 'selectors/selectVenueById'
import venuesSelector from 'selectors/venues'

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { offerId },
    },
    query,
  } = ownProps
  const queryParams = query.parse()

  const providers = selectProviders(state)

  const offer = selectOfferById(state, offerId)

  const eventId = get(offer, 'eventId')
  const event = selectEventById(state, eventId)

  const thingId = get(offer, 'thingId')
  const thing = selectThingById(state, thingId)

  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = formVenueId || queryParams.venueId

  const venue = selectVenueById(state, venueId)

  const isVirtual = get(venue, 'isVirtual')
  const types = typesSelector(state, isVirtual)

  const offerTypeValue =
    get(state, 'form.offer.type') ||
    get(event, 'offerType.value') ||
    get(thing, 'offerType.value')

  const selectedOfferType = typeSelector(state, isVirtual, offerTypeValue)

  const formOffererId = get(state, 'form.offer.offererId')
  let offererId = formOffererId || queryParams.offererId

  const venues = venuesSelector(state, offererId, selectedOfferType)

  offererId = offererId || get(venue, 'managingOffererId')

  const offerers = offerersSelector(state)
  const offerer = selectOffererById(state, offererId)

  const stocks = selectStocksByOfferId(state, offerId)

  const url =
    get(state, 'form.offer.url') || get(event, 'url') || get(thing, 'url')

  const hasEventOrThing = event || thing

  const eventOrThingPatch = eventOrThingPatchSelector(
    state,
    event,
    thing,
    offer,
    offerer,
    venue
  )
  const extraData = get(state, 'form.offer.extraData') || {}

  const musicSubOptions =
    extraData.musicType && selectMusicSubOptionsByMusicType(extraData.musicType)
  const showSubOptions =
    extraData.showType && selectShowSubOptionsByShowType(extraData.showType)

  const offerTypeError = get(state, 'errors.offer.type')

  return {
    event,
    eventOrThingPatch,
    formOffererId,
    formVenueId,
    hasEventOrThing,
    musicSubOptions,
    offer,
    offerer,
    offerers,
    offerTypeError,
    providers,
    showSubOptions,
    stocks,
    thing,
    types,
    selectedOfferType,
    url,
    venue,
    venues,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withQueryRouter,
  connect(mapStateToProps)
)(RawOffer)
