import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { DEFAULT_THUMB_URL } from '../../../utils/thumb'
import Recto from './Recto'
import { selectBookingById } from '../../../redux/selectors/data/bookingsSelectors'
import { selectStockById } from '../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../redux/selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match, recommendation } = ownProps
  const { params } = match
  const { bookingId, offerId } = params

  if (bookingId) {
    return findThumbByBookingId(state, bookingId)
  } else {
    return findThumbByOfferId(state, offerId, match, recommendation)
  }
}

export const findThumbByBookingId = (state, bookingId) => {
  let thumbUrl = ''

  const booking = selectBookingById(state, bookingId)
  const { stockId = '' } = booking
  const stock = selectStockById(state, stockId)
  const { offerId = '' } = stock || {}
  const offer = selectOfferById(state, offerId)

  thumbUrl = offer.thumbUrl ? offer.thumbUrl : DEFAULT_THUMB_URL

  return {
    thumbUrl,
  }
}

export const findThumbByOfferId = (state, offerId, match, recommendation) => {
  if (recommendation) {
    return {
      thumbUrl: recommendation && recommendation.thumbUrl,
    }
  }

  const offer = selectOfferById(state, offerId)
  if (offer) {
    return {
      thumbUrl: offer.thumbUrl ? offer.thumbUrl : DEFAULT_THUMB_URL,
    }
  }

  return {
    thumbUrl: DEFAULT_THUMB_URL,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps),
)(Recto)
