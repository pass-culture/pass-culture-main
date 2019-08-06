import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import BookingItem from './BookingItem'
import getIsFinished from '../../../../../../helpers/getIsFinished'
import selectMediationById from '../../../../../../selectors/selectMediationById'
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
  const { isCancelled, isUsed, recommendationId, stock } = booking
  const { beginningDatetime } = stock
  const humanizeRelativeBeginningDate =
    beginningDatetime && getHumanizeRelativeDate(beginningDatetime)

  const recommendation = selectRecommendationById(state, recommendationId) || {}
  const mediation = selectMediationById(state, recommendation.mediationId)
  const offer = selectOfferById(state, booking.stock.offerId)

  const isFinished = getIsFinished(offer, mediation, booking)

  const ribbon = ribbonLabelAndType(isUsed, isCancelled, isFinished, humanizeRelativeBeginningDate)

  return {
    isFinished,
    mediation,
    offer,
    recommendation,
    ribbon,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(BookingItem)
