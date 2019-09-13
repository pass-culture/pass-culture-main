import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import VersoContentOffer from './VersoContentOffer'
import selectMusicTypeByCode from './selectors/selectMusicTypeByCode'
import selectMusicSubTypeByCodeAndSubCode from './selectors/selectMusicSubTypeByCodeAndSubCode'
import selectShowTypeByCode from './selectors/selectShowTypeByCode'
import selectShowSubTypeByCodeAndSubCode from './selectors/selectShowSubTypeByCodeAndSubCode'
import selectBookables from '../../../../../selectors/selectBookables'
import selectBookingByRouterMatch from '../../../../../selectors/selectBookingByRouterMatch'
import selectDistanceByRouterMatch from '../../../../../selectors/selectDistanceByRouterMatch'
import selectIsFinishedByRouterMatch from '../../../../../selectors/selectIsFinishedByRouterMatch'
import selectOfferByRouterMatch from '../../../../../selectors/selectOfferByRouterMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const bookables = selectBookables(state, offer)
  const isFinished = selectIsFinishedByRouterMatch(state, match)
  const { product } = offer || {}
  const { extraData } = product || {}
  const {
    musicSubType: musicSubCode,
    musicType: musicCode,
    showSubType: showSubCode,
    showType: showCode,
  } = extraData || {}
  const musicType = selectMusicTypeByCode(state, musicCode)
  const showType = selectShowTypeByCode(state, showCode)
  const musicSubType = selectMusicSubTypeByCodeAndSubCode(state, musicCode, musicSubCode)
  const showSubType = selectShowSubTypeByCodeAndSubCode(state, showCode, showSubCode)
  const {
    data: { musicTypes, showTypes },
  } = state
  const booking = selectBookingByRouterMatch(state, match)
  const distance = selectDistanceByRouterMatch(state, match)
  const isCancelled = booking && booking.isCancelled

  return {
    bookables,
    booking,
    distance,
    isCancelled,
    isFinished,
    musicSubType,
    musicType,
    musicTypes,
    offer,
    showSubType,
    showType,
    showTypes,
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
