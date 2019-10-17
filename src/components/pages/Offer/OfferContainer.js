import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Offer from './Offer'
import { withRequiredLogin } from '../../hocs'
import withTracking from '../../hocs/withTracking'

import selectFormInitialValuesByProductAndOfferAndOffererAndVenue from './utils/selectFormInitialValuesByProductAndOfferAndOffererAndVenue'
import selectOfferById from '../../../selectors/selectOfferById'
import { selectOffererById } from '../../../selectors/data/offerersSelectors'
import selectProductById from '../../../selectors/selectProductById'
import selectProviders from '../../../selectors/selectProviders'
import selectMusicSubOptionsByMusicType from '../../../selectors/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from '../../../selectors/selectShowSubOptionsByShowType'
import selectStocksByOfferId from '../../../selectors/selectStocksByOfferId'
import selectTypesByIsVenueVirtual from '../../../selectors/selectTypesByIsVenueVirtual'
import selectTypeByIsVenueVirtualAndOfferTypeValue from '../../../selectors/selectTypeByIsVenueVirtualAndOfferTypeValue'
import {
  selectVenueById,
  selectVenuesByOffererIdAndOfferType,
} from '../../../selectors/data/venuesSelectors'
import { selectOfferers } from '../../../selectors/data/offerersSelectors'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'

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
  const isEditableOffer = get(offer, 'isEditable')
  const productId = get(offer, 'productId')
  const product = selectProductById(state, productId)
  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = formVenueId || translatedQueryParams.venueId
  const venue = selectVenueById(state, venueId)
  const isVenueVirtual = get(venue, 'isVirtual')
  const types = selectTypesByIsVenueVirtual(state, isVenueVirtual)
  const offerTypeValue = get(state, 'form.offer.type') || get(product, 'offerType.value')
  const selectedOfferType = selectTypeByIsVenueVirtualAndOfferTypeValue(
    state,
    isVenueVirtual,
    offerTypeValue
  )
  const formOffererId = get(state, 'form.offer.offererId')
  let offererId = formOffererId || translatedQueryParams.offererId
  offererId = offererId || get(venue, 'managingOffererId')

  const venues = selectVenuesByOffererIdAndOfferType(state, offererId, selectedOfferType)

  const offerers = selectOfferers(state)
  const offerer = selectOffererById(state, offererId)
  const stocks = selectStocksByOfferId(state, offerId)
  const url = get(state, 'form.offer.url') || get(product, 'url')

  // should return value object
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
  const showSubOptions = extraData.showType && selectShowSubOptionsByShowType(extraData.showType)
  const offerTypeError = get(state, 'errors.offer.type')

  const isFeatureDisabled = selectIsFeatureDisabled(state, 'DUO_OFFER')

  return {
    formInitialValues,
    formOffererId,
    formVenueId,
    isEditableOffer,
    isFeatureDisabled,
    musicSubOptions,
    offer,
    offerer,
    offerers,
    offerTypeError,
    providers,
    selectedOfferType,
    showSubOptions,
    stocks,
    types,
    url,
    venue,
    venues,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackCreateOffer: createdOfferId => {
      ownProps.tracking.trackEvent({ action: 'createOffer', name: createdOfferId })
    },
    trackModifyOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'modifyOffer', name: offerId })
    },
  }
}

export default compose(
  withTracking('Offer'),
  withRequiredLogin,
  connect(
    mapStateToProps,
    null,
    mergeProps
  )
)(Offer)
