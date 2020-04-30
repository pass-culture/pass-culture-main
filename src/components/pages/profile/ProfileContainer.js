import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from '../../../redux/selectors/data/usersSelectors'

import Profile from './Profile'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Profile)
