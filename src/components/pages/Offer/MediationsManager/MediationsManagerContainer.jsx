import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import MediationsManager from './MediationsManager'
import selectMediationsByOfferId from '../../../../selectors/selectMediationsByOfferId'
import selectOfferById from '../../../../selectors/selectOfferById'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
  } = ownProps
  return {
    mediations: selectMediationsByOfferId(state, offerId),
    notification: state.notification,
    offer: selectOfferById(state, offerId),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MediationsManager)
