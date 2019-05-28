import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs/with-login'
import Profil from './Profil'
import { selectCurrentUser } from 'with-login'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(Profil)
