import { compose } from 'redux'
import { connect } from 'react-redux'

import Profil from './Profil'
import { selectCurrentUser } from 'with-login'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(Profil)
