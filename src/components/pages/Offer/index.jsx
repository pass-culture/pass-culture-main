import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RawOffer from './RawOffer'
import selectEventOrThingPatchByEventAndThingAndOfferAndOffererAndVenue from './selectEventOrThingPatchByEventAndThingAndOfferAndOffererAndVenue'
import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from 'components/hocs'
import selectEventById from 'selectors/selectEventById'
import selectOfferById from 'selectors/selectOfferById'
import selectOffererById from 'selectors/selectOffererById'
import selectProviders from 'selectors/selectProviders'
import selectMusicSubOptionsByMusicType from 'selectors/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from 'selectors/selectShowSubOptionsByShowType'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import selectThingById from 'selectors/selectThingById'
import selectTypesByIsVenueVirtual from 'selectors/selectTypesByIsVenueVirtual'
import selectTypeByIsVenueVirtualAndOfferTypeValue from 'selectors/selectTypeByIsVenueVirtualAndOfferTypeValue'
import selectVenueById from 'selectors/selectVenueById'
import selectVenuesByOffererIdAndOfferType from 'selectors/selectVenuesByOffererIdAndOfferType'
import { translateQueryParamsToApiParams } from '../../../utils/translate'

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { offerId },
    },
    query,
  } = ownProps
  const queryParams = translateQueryParamsToApiParams(query.parse())

  const providers = selectProviders(state)

  const offer = selectOfferById(state, offerId)

  const eventId = get(offer, 'eventId')
  const event = selectEventById(state, eventId)

  const thingId = get(offer, 'thingId')
  const thing = selectThingById(state, thingId)

  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = formVenueId || queryParams.venueId

  const venue = selectVenueById(state, venueId)

  const isVenueVirtual = get(venue, 'isVirtual')
  const types = selectTypesByIsVenueVirtual(state, isVenueVirtual)

  const offerTypeValue =
    get(state, 'form.offer.type') ||
    get(event, 'offerType.value') ||
    get(thing, 'offerType.value')

  const selectedOfferType = selectTypeByIsVenueVirtualAndOfferTypeValue(
    state,
    isVenueVirtual,
    offerTypeValue
  )

  const formOffererId = get(state, 'form.offer.offererId')
  let offererId = formOffererId || queryParams.offererId

  const venues = selectVenuesByOffererIdAndOfferType(
    state,
    offererId,
    selectedOfferType
  )

  offererId = offererId || get(venue, 'managingOffererId')

  const offerers = state.data.offerers
  const offerer = selectOffererById(state, offererId)

  const stocks = selectStocksByOfferId(state, offerId)

  const url =
    get(state, 'form.offer.url') || get(event, 'url') || get(thing, 'url')

  const hasEventOrThing = event || thing

  const eventOrThingPatch = selectEventOrThingPatchByEventAndThingAndOfferAndOffererAndVenue(
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
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawOffer)
