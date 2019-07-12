import Desk from './Desk'
import { compose } from 'redux'
import { connect } from 'react-redux'

import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect()
)(Desk)
