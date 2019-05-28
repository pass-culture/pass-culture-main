import Desk from './Desk'
import { compose } from 'redux'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs/with-login'
import { connect } from 'react-redux'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect()
)(Desk)
