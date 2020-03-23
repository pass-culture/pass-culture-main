import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from '../../hocs/with-login/with-login'

import Profile from './Profile'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Profile)
