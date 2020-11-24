import { connect } from 'react-redux'

import { selectOfferById } from 'store/offers/selectors'
import { selectMediationsByOfferId } from 'store/selectors/data/mediationsSelectors'

import MediationsManager from './MediationsManager'

export const mapStateToProps = (state, ownProps) => {
  const { offerId } = ownProps
  // TODO: Supprimer après la suppression des anciennes pages de détails des offres
  const mediations = ownProps.offer?.mediations || selectMediationsByOfferId(state, offerId)

  return {
    mediations: mediations,
    hasMediations: mediations.length > 0,
    atLeastOneActiveMediation: mediations.some(mediation => mediation.isActive),
    notification: state.notification,
    // TODO: Supprimer après la suppression des anciennes pages de détails des offres
    offer: ownProps.offer || selectOfferById(state, offerId),
  }
}

export default connect(mapStateToProps)(MediationsManager)
