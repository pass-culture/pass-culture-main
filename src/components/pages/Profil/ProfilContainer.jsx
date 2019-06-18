import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'with-react-redux-login'

import Profil from './Profil'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(Profil)
