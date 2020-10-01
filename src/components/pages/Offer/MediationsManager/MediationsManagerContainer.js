import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import MediationsManager from './MediationsManager'
import { selectMediationsByOfferId } from 'store/selectors/data/mediationsSelectors'
import { selectOfferById } from 'store/selectors/data/offersSelectors'

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

export default compose(withRouter, connect(mapStateToProps))(MediationsManager)
