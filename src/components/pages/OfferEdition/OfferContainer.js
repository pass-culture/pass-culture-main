import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Offer from './Offer'
import { withRequiredLogin } from '../../hocs'
import withTracking from '../../hocs/withTracking'

import selectFormInitialValuesByProductAndOfferAndOffererAndVenue from './utils/selectFormInitialValuesByProductAndOfferAndOffererAndVenue'
import { selectOffererById } from '../../../selectors/data/offerersSelectors'
import { selectProductById } from '../../../selectors/data/productsSelectors'
import { selectMusicSubOptionsByMusicType } from '../../../utils/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from '../../../utils/selectShowSubOptionsByShowType'
import { selectTypesByIsVenueVirtual } from '../../../selectors/data/typesSelectors'
import selectTypeByIsVenueVirtualAndOfferTypeValue from './selectTypeByIsVenueVirtualAndOfferTypeValue'
import {
  selectVenueById,
  selectVenuesByOffererIdAndOfferType,
} from '../../../selectors/data/venuesSelectors'
import { selectOfferers } from '../../../selectors/data/offerersSelectors'
import { mergeForm, showNotification } from 'pass-culture-shared'
import { selectStocksByOfferId } from '../../../selectors/data/stocksSelectors'
import { selectProviders } from '../../../selectors/data/providersSelectors'
import { selectOfferById } from '../../../selectors/data/offersSelectors'

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
  const venueId = offer ? offer.venueId : ''
  const venue = selectVenueById(state, venueId)
  const isVenueVirtual = get(venue, 'isVirtual')
  const types = selectTypesByIsVenueVirtual(state, isVenueVirtual)
  const offerTypeValue = get(state, 'form.offer.type') || get(offer, 'type')
  const selectedOfferType = selectTypeByIsVenueVirtualAndOfferTypeValue(
    state,
    isVenueVirtual,
    offerTypeValue
  )
  const formOffererId = get(state, 'form.offer.offererId')

  let offererId = formOffererId || translatedQueryParams.offererId

  offererId = offererId || get(venue, 'managingOffererId')

  const venuesMatchingOfferType = selectVenuesByOffererIdAndOfferType(
    state,
    offererId,
    selectedOfferType
  )

  const offerers = selectOfferers(state)
  const offerer = selectOffererById(state, offererId)
  const stocks = selectStocksByOfferId(state, offerId)
  const url = get(state, 'form.offer.url') || get(offer, 'url')

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

  return {
    formInitialValues,
    formOffererId,
    formVenueId,
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
    venuesMatchingOfferType,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackModifyOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'modifyOffer', name: offerId })
    },
  }
}

export const mapDispatchToProps = dispatch => ({
  updateFormSetIsDuo: isDuo => {
    dispatch(
      mergeForm('offer', {
        isDuo: isDuo,
      })
    )
  },

  showOfferModificationValidationNotification: () => {
    dispatch(
      showNotification({
        text:
          'Votre offre a bien été modifiée. L’offre peut mettre quelques minutes pour être disponible dans l’application.',
        type: 'success',
      })
    )
  },
})

export default compose(
  withTracking('Offer'),
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Offer)
