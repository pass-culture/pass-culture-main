import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectBookingById } from '../../../../../redux/selectors/data/bookingsSelectors'
import { selectFavoriteByOfferId } from '../../../../../redux/selectors/data/favoritesSelectors'
import { selectMediationByOfferId } from '../../../../../redux/selectors/data/mediationsSelectors'
import { selectStockById } from '../../../../../redux/selectors/data/stocksSelectors'
import { requestData } from '../../../../../utils/fetch-normalize-data/requestData'
import withTracking from '../../../../hocs/withTracking'

import Favorite from './Favorite'

const API_PATH_TO_FAVORITES_ENDPOINT = '/favorites'

export const apiPath = (isFavorite, offerId) => {
  const chunk = isFavorite ? `/${offerId}` : ''

  return `${API_PATH_TO_FAVORITES_ENDPOINT}${chunk}`
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  let { bookingId, offerId } = params

  if (bookingId) {
    const booking = selectBookingById(state, bookingId)
    const { stockId } = booking
    const stock = selectStockById(state, stockId)
    const { offerId: offerIdFromStock } = stock
    offerId = offerIdFromStock
  }
  const mediation = selectMediationByOfferId(state, offerId) || {}
  const { id: mediationId } = mediation
  const favorite = selectFavoriteByOfferId(state, offerId)
  const isFavorite = favorite !== undefined

  return {
    isFavorite,
    mediationId,
    offerId,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleFavorite: (offerId, mediationId, isFavorite, showFailModal, handleSuccess) => () => {
    dispatch(
      requestData({
        apiPath: apiPath(isFavorite, offerId),
        body: {
          mediationId,
          offerId,
        },
        handleFail: showFailModal,
        handleSuccess,
        method: isFavorite ? 'DELETE' : 'POST',
      })
    )
  },
  loadFavorites: () => {
    dispatch(
      requestData({
        apiPath: API_PATH_TO_FAVORITES_ENDPOINT,
      })
    )
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => ({
  ...stateProps,
  ...dispatchProps,
  ...ownProps,
  trackAddToFavoritesFromHome: (moduleName, offerId) => {
    ownProps.tracking.trackEvent({
      action: 'AddFavorite_FromHomepage',
      name: `Module name: ${moduleName} - Offer id: ${offerId}`,
    })
  },
  trackAddToFavoritesFromSearch: offerId => {
    ownProps.tracking.trackEvent({ action: 'AddFavorite_FromSearch', name: offerId })
  },
  trackAddToFavoritesFromBooking: offerId => {
    ownProps.tracking.trackEvent({ action: 'AddFavorite_FromBooking', name: offerId })
  },
  trackAddToFavoritesFromOfferLink: offerId => {
    ownProps.tracking.trackEvent({ action: 'AddFavorite_FromOfferLink', name: offerId })
  },
})

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(Favorite)
