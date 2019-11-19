import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectMediationById } from '../../../../../../selectors/data/mediationsSelectors'
import { selectOfferById } from '../../../../../../selectors/data/offersSelectors'
import { selectRecommendationById } from '../../../../../../selectors/data/recommendationsSelectors'
import { selectStockById } from '../../../../../../selectors/data/stocksSelectors'
import getHumanizeRelativeDate from '../../../../../../utils/date/getHumanizeRelativeDate'
import withTracking from '../../../../../hocs/withTracking'
import selectIsFeatureDisabled from '../../../../../router/selectors/selectIsFeatureDisabled'
import BookingItem from './BookingItem'

export const ribbonLabelAndType = (
  isUsed,
  isCancelled,
  isPhysical,
  isDigital,
  isEventExpired,
  humanizeRelativeDate = ''
) => {
  if (isUsed) {
    if (isPhysical) {
      return {
        label: 'Retiré',
        type: 'finished',
      }
    }
    if (isDigital) {
      return {
        label: 'Utilisé',
        type: 'finished',
      }
    }
  }
  if (!isCancelled) {
    if (isEventExpired) {
      return {
        label: 'Terminé',
        type: 'finished',
      }
    }
    if (humanizeRelativeDate === 'Aujourd’hui') {
      return {
        label: 'Aujourd’hui',
        type: 'today',
      }
    }
    if (humanizeRelativeDate === 'Demain') {
      return {
        label: 'Demain',
        type: 'tomorrow',
      }
    }
  }
  if (isCancelled) {
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
  const { isDigital, isEvent } = offer
  const { isEventExpired } = booking
  const isPhysical = !isDigital && !isEvent
  const ribbon = ribbonLabelAndType(
    isUsed,
    isCancelled,
    isPhysical,
    isDigital,
    isEventExpired,
    humanizeRelativeBeginningDate
  )
  const isQrCodeFeatureDisabled = selectIsFeatureDisabled(state, 'QR_CODE')

  return {
    isQrCodeFeatureDisabled,
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
