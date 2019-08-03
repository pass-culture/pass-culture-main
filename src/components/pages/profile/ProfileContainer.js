import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import Profile from './Profile'
import { withRequiredLogin } from '../../hocs'

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Profile)
