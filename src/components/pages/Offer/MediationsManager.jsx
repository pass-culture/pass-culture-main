import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import mediationsSelector from '../../../selectors/mediations'
import offerSelector from '../../../selectors/offer'
import RawMediationManager from './RawMediationsManager'

function mapStateToProps(state, ownProps) {
  return {
    mediations: mediationsSelector(state, ownProps.match.params.offerId),
    notification: state.notification,
    offer: offerSelector(state, ownProps.match.params.offerId),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawMediationManager)
