import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Offer from './Offer'
import selectFormInitialValuesByProductAndOfferAndOffererAndVenue from './utils/selectFormInitialValuesByProductAndOfferAndOffererAndVenue'
import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from '../../hocs'
import selectOfferById from '../../../selectors/selectOfferById'
import selectOffererById from '../../../selectors/selectOffererById'
import selectProductById from '../../../selectors/selectProductById'
import selectProviders from '../../../selectors/selectProviders'
import selectMusicSubOptionsByMusicType from '../../../selectors/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from '../../../selectors/selectShowSubOptionsByShowType'
import selectStocksByOfferId from '../../../selectors/selectStocksByOfferId'
import selectTypesByIsVenueVirtual from '../../../selectors/selectTypesByIsVenueVirtual'
import selectTypeByIsVenueVirtualAndOfferTypeValue from '../../../selectors/selectTypeByIsVenueVirtualAndOfferTypeValue'
import selectVenueById from '../../../selectors/selectVenueById'
import selectVenuesByOffererIdAndOfferType from '../../../selectors/selectVenuesByOffererIdAndOfferType'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
    query,
  } = ownProps

  const translatedQueryParams = query.translate()
  const providers = selectProviders(state)
  const offer = selectOfferById(state, offerId)
  const productId = get(offer, 'productId')
  const product = selectProductById(state, productId)
  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = formVenueId || translatedQueryParams.venueId
  const venue = selectVenueById(state, venueId)
  const isVenueVirtual = get(venue, 'isVirtual')
  const types = selectTypesByIsVenueVirtual(state, isVenueVirtual)
  const offerTypeValue =
    get(state, 'form.offer.type') || get(product, 'offerType.value')
  const selectedOfferType = selectTypeByIsVenueVirtualAndOfferTypeValue(
    state,
    isVenueVirtual,
    offerTypeValue
  )
  const formOffererId = get(state, 'form.offer.offererId')
  let offererId = formOffererId || translatedQueryParams.offererId
  offererId = offererId || get(venue, 'managingOffererId')

  const venues = selectVenuesByOffererIdAndOfferType(
    state,
    offererId,
    selectedOfferType
  )

  const offerers = state.data.offerers
  const offerer = selectOffererById(state, offererId)
  const stocks = selectStocksByOfferId(state, offerId)
  const url = get(state, 'form.offer.url') || get(product, 'url')

  const formInitialValues = selectFormInitialValuesByProductAndOfferAndOffererAndVenue(
    state,
    product,
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
    formInitialValues,
    formOffererId,
    formVenueId,
    musicSubOptions,
    offer,
    offerer,
    offerers,
    offerTypeError,
    product,
    providers,
    showSubOptions,
    stocks,
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
)(Offer)
