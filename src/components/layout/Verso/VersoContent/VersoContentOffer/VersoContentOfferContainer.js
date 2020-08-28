import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectBookingByRouterMatch } from '../../../../../redux/selectors/data/bookingsSelectors'
import { selectOfferByRouterMatch } from '../../../../../redux/selectors/data/offersSelectors'
import { selectBookables } from '../../../../../redux/selectors/data/stocksSelectors'
import { selectDistanceByRouterMatch, selectUserGeolocation } from '../../../../../redux/selectors/geolocationSelectors'
import { requestData } from '../../../../../utils/fetch-normalize-data/requestData'
import getStyle from './utils/getStyle'
import VersoContentOffer from './VersoContentOffer'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const bookables = selectBookables(state, offer)
  const isBookable = offer.isBookable
  const { extraData } = offer || {}
  const style = getStyle(state, extraData)
  const booking = selectBookingByRouterMatch(state, match)
  const distance = selectDistanceByRouterMatch(state, match)
  const userGeolocation = selectUserGeolocation(state)
  const isCancelled = booking && booking.isCancelled

  return {
    bookables,
    booking,
    distance,
    isCancelled,
    isBookable,
    offer,
    style,
    userGeolocation,
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  handleRequestMusicAndShowTypes: () => {
    const { musicTypes, showTypes } = ownProps

    if (!musicTypes) {
      dispatch(
        requestData({
          apiPath: '/musicTypes',
        })
      )
    }

    if (!showTypes) {
      dispatch(
        requestData({
          apiPath: '/showTypes',
        })
      )
    }
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(VersoContentOffer)
