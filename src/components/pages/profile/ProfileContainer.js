import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from '../../../selectors/data/usersSelectors'

import Profile from './Profile'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Profile)
