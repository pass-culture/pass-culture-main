import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import RawOfferers from './RawOfferers'
import offerersSelector, {
  getPendingOfferers,
} from '../../../selectors/offerers'

function mapStateToProps(state, ownProps) {
  return {
    pendingOfferers: getPendingOfferers(state),
    offerers: offerersSelector(state),
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withQueryRouter,
  connect(mapStateToProps)
)(RawOfferers)
