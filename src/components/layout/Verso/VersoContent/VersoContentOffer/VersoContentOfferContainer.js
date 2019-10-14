import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import VersoContentOffer from './VersoContentOffer'
import getStyle from './utils/getStyle'
import selectBookables from '../../../../../selectors/selectBookables'
import selectBookingByRouterMatch from '../../../../../selectors/selectBookingByRouterMatch'
import selectDistanceByRouterMatch from '../../../../../selectors/selectDistanceByRouterMatch'
import selectIsNotBookableByRouterMatch from '../../../../../selectors/selectIsNotBookableByRouterMatch'
import selectOfferByRouterMatch from '../../../../../selectors/selectOfferByRouterMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const bookables = selectBookables(state, offer)
  const isNotBookable = selectIsNotBookableByRouterMatch(state, match)
  const { product } = offer || {}
  const { extraData } = product || {}
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
