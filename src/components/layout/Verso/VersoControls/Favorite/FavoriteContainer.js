import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'redux-thunk-data'
import { compose } from 'redux'

import Favorite from './Favorite'
import { favoriteNormalizer } from '../../../../../utils/normalizers'
import { selectFavoriteByOfferId } from '../../../../../selectors/data/favoritesSelectors'
import { selectMediationByOfferId } from '../../../../../selectors/data/mediationsSelectors'
import { selectBookingById } from '../../../../../selectors/data/bookingsSelectors'
import { selectStockById } from '../../../../../selectors/data/stocksSelectors'

const API_PATH_TO_FAVORITES_ENDPOINT = '/favorites'

export const apiPath = (isFavorite, offerId) => {
  const chunk = isFavorite ? `/${offerId}` : ''

  return `${API_PATH_TO_FAVORITES_ENDPOINT}${chunk}`
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  let { bookingId, offerId } = params

  if (bookingId && bookingId !== 'menu') {
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
        normalizer: favoriteNormalizer,
      })
    )
  },
  loadFavorites: () => {
    dispatch(
      requestData({
        apiPath: API_PATH_TO_FAVORITES_ENDPOINT,
        normalizer: favoriteNormalizer,
      })
    )
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Favorite)
