import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import VersoContentOffer from './VersoContentOffer'
import getStyle from './utils/getStyle'
import { selectBookingByRouterMatch } from '../../../../../selectors/data/bookingsSelectors'
import { selectOfferByRouterMatch } from '../../../../../selectors/data/offersSelectors'
import { selectDistanceByRouterMatch } from '../../../../../selectors/geolocationSelectors'
import {
  selectBookables,
  selectIsNotBookableByRouterMatch,
} from '../../../../../selectors/data/bookablesSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const bookables = selectBookables(state, offer)
  const isNotBookable = selectIsNotBookableByRouterMatch(state, match)
  const { extraData } = offer || {}
  const style = getStyle(state, extraData)
  const booking = selectBookingByRouterMatch(state, match)
  const distance = selectDistanceByRouterMatch(state, match)
  const isCancelled = booking && booking.isCancelled

  return {
    bookables,
    booking,
    distance,
    isCancelled,
    isNotBookable,
    offer,
    style,
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
