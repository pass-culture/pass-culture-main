import { connect } from 'react-redux'

import { selectMediationsByOfferId } from 'store/selectors/data/mediationsSelectors'
import { selectOfferById } from 'store/selectors/data/offersSelectors'

import MediationsManager from './MediationsManager'

export const mapStateToProps = (state, ownProps) => {
  const { offerId } = ownProps
  const mediations = selectMediationsByOfferId(state, offerId)

  return {
    mediations: mediations,
    hasMediations: mediations.length > 0,
    atLeastOneActiveMediation: mediations.some(mediation => mediation.isActive),
    notification: state.notification,
    offer: selectOfferById(state, offerId),
  }
}

export default connect(mapStateToProps)(MediationsManager)
