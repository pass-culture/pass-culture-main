import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import withTracking from 'components/hocs/withTracking'
import { selectOfferById } from 'store/offers/selectors'
import { loadOffer } from 'store/offers/thunks'
import { mergeForm } from 'store/reducers/form'
import { showNotificationV1 } from 'store/reducers/notificationReducer'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectOfferers } from 'store/selectors/data/offerersSelectors'
import { selectProductById } from 'store/selectors/data/productsSelectors'
import { selectProviders } from 'store/selectors/data/providersSelectors'
import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'
import { selectTypesByIsVenueVirtual } from 'store/selectors/data/typesSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import {
  selectVenueById,
  selectVenuesByOffererIdAndOfferType,
} from 'store/selectors/data/venuesSelectors'
import { selectMusicSubOptionsByMusicType } from 'utils/selectMusicSubOptionsByMusicType'
import selectShowSubOptionsByShowType from 'utils/selectShowSubOptionsByShowType'

import selectFormInitialValuesByProductAndOfferAndOffererAndVenue from '../selectors/selectFormInitialValuesByProductAndOfferAndOffererAndVenue'
import selectTypeByIsVenueVirtualAndOfferTypeValue from '../selectors/selectTypeByIsVenueVirtualAndOfferTypeValue'

import OfferCreation from './OfferCreation'

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
  const offerVenueId = get(offer, 'venueId')
  const formVenueId = get(state, 'form.offer.venueId')
  const venueId = offerVenueId || formVenueId || translatedQueryParams.venueId
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
  const offerer = venue
    ? venue.managingOfferer || selectOffererById(state, offererId)
    : selectOffererById(state, offererId)
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
    currentUser: selectCurrentUser(state),
    formInitialValues,
    formOffererId,
    formVenueId,
    isEditableOffer,
    musicSubOptions,
    offer,
    offerer,
    offerers,
    offersSearchFilters: state.offers.searchFilters,
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

export const mapDispatchToProps = dispatch => ({
  dispatch,
  loadOffer: offerId => dispatch(loadOffer(offerId)),
  showValidationNotification: () => {
    dispatch(
      showNotificationV1({
        text:
          'Votre offre a bien été créée. Cette offre peut mettre quelques minutes pour être disponible dans l’application.',
        type: 'success',
      })
    )
  },

  updateFormSetIsDuo: isDuo => {
    dispatch(
      mergeForm('offer', {
        isDuo: isDuo,
      })
    )
  },
})

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
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(OfferCreation)
