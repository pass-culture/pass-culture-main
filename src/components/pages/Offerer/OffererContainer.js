import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'
import mapStateToProps from './mapStateToProps'
import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from '../../hocs'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offerer)
