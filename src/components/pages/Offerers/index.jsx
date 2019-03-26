import { connect } from 'react-redux'
import { compose } from 'redux'

import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from 'components/hocs'
import RawOfferers from './RawOfferers'

function mapStateToProps(state, ownProps) {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawOfferers)
