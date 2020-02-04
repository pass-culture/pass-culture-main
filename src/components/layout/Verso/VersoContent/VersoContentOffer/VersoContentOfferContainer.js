import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import {
  selectBookables,
  selectBookingByRouterMatch
} from '../../../../../selectors/data/bookingsSelectors'
import { selectOfferByRouterMatch } from '../../../../../selectors/data/offersSelectors'
import { selectDistanceByRouterMatch } from '../../../../../selectors/geolocationSelectors'
import { selectIsNotBookableByRouterMatch } from '../../../../../selectors/isNotBookableSelector'
import { selectUserGeolocation } from '../../../../../selectors/geolocationSelectors'
import getStyle from './utils/getStyle'
import VersoContentOffer from './VersoContentOffer'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const bookables = selectBookables(state, offer)
  const isNotBookable = selectIsNotBookableByRouterMatch(state, match)
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
    isNotBookable,
    offer,
    style,
    userGeolocation
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  handleRequestMusicAndShowTypes: () => {
    const { musicTypes, showTypes } = ownProps

    if (!musicTypes) {
      dispatch(
        requestData({
          apiPath: '/musicTypes'
        })
      )
    }

    if (!showTypes) {
      dispatch(
        requestData({
          apiPath: '/showTypes'
        })
      )
    }
  }
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(VersoContentOffer)
