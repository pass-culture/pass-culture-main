import { connect } from 'react-redux'
import { compose } from 'redux'

import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from 'components/hocs'
import Offerers from './Offerers'

export function mapStateToProps(state) {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offerers)
