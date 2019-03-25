import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import RawOfferers from './RawOfferers'

function mapStateToProps(state, ownProps) {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withQueryRouter,
  connect(mapStateToProps)
)(RawOfferers)
