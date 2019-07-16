import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'
import mapStateToProps from './mapStateToProps'
import withFrenchQueryRouter from '../../hocs/withFrenchQueryRouter'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offerer)
