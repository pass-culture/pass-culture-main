import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { withRedirectToOffersWhenAlreadyAuthenticated } from '../../hocs/with-login/withRedirectToOffersWhenAlreadyAuthenticated'
import Signup from './Signup'

export default compose(
  withRedirectToOffersWhenAlreadyAuthenticated,
  withRouter
)(Signup)
