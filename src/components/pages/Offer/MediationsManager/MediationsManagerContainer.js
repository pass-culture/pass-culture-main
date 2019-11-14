import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { closeNotification, showNotification } from 'pass-culture-shared'

import MediationsManager from './MediationsManager'
import { selectMediationsByOfferId } from '../../../../selectors/data/mediationsSelectors'
import { selectOfferById } from '../../../../selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
  } = ownProps
  const mediations = selectMediationsByOfferId(state, offerId)

  return {
    mediations: mediations,
    hasMediations: mediations.length > 0,
    atLeastOneActiveMediation: mediations.some(mediation => mediation.isActive),
    notification: state.notification,
    offer: selectOfferById(state, offerId),
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    showNotification: notif => {
      dispatch(showNotification(notif))
    },
    closeNotification: () => {
      dispatch(closeNotification())
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MediationsManager)
