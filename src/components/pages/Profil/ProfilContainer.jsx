import { compose } from 'redux'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs/with-login'
import Profil from './Profil'
import { selectCurrentUser } from 'with-login'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

PropTypes.propTypes = {
  currentUser: PropTypes.object.isRequired,
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(Profil)
