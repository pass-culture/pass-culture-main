import Desk from './Desk'
import { compose } from 'redux'
import { connect } from 'react-redux'

import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect()
)(Desk)
