import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import withTracking from '../../../../../hocs/withTracking'
import BookingItem from './BookingItem'

import getIsFinished from '../../../../../../helpers/getIsFinished'
import selectMediationById from '../../../../../../selectors/selectMediationById'
import selectStockById from '../../../../../../selectors/selectStockById'
import selectOfferById from '../../../../../../selectors/selectOfferById'
import selectRecommendationById from '../../../../../../selectors/selectRecommendationById'
import getHumanizeRelativeDate from '../../../../../../utils/date/getHumanizeRelativeDate'

export const ribbonLabelAndType = (isUsed, isCancelled, isFinished, humanizeRelativeDate = '') => {
  if (isUsed) {
    return {
      label: 'Terminé',
      type: 'finished',
    }
  }

  if (!isCancelled && humanizeRelativeDate === 'Aujourd’hui') {
    return {
      label: 'Aujourd’hui',
      type: 'today',
    }
  } else if (!isCancelled && humanizeRelativeDate === 'Demain') {
    return {
      label: 'Demain',
      type: 'tomorrow',
    }
  } else if (!isCancelled && isFinished) {
    return {
      label: 'Terminé',
      type: 'finished',
    }
  } else if (isCancelled) {
    return {
      label: 'Annulé',
      type: 'cancelled',
    }
  }

  return null
}

export const mapStateToProps = (state, ownProps) => {
  const { booking } = ownProps
  const { isCancelled, isUsed, recommendationId, stockId } = booking
  const stock = selectStockById(state, stockId)
  const { beginningDatetime } = stock
  const humanizeRelativeBeginningDate =
    beginningDatetime && getHumanizeRelativeDate(beginningDatetime)
  const recommendation = selectRecommendationById(state, recommendationId) || {}
  const mediation = selectMediationById(state, recommendation.mediationId)
  const offer = selectOfferById(state, stock.offerId)
  const isFinished = getIsFinished(offer, mediation, booking)
  const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished, humanizeRelativeBeginningDate)

  return {
    isFinished,
    mediation,
    offer,
    recommendation,
    ribbon,
    stock,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { offer: { id: offerId } = {} } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackConsultOffer: () => {
      ownProps.tracking.trackEvent({ action: 'consultOffer', name: offerId })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(
    mapStateToProps,
    {},
    mergeProps
  )
)(BookingItem)
