import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectCurrentUser } from '../../../redux/selectors/currentUserSelector'

import Profile from './Profile'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

const mapStateToProps = state => ({
  user: selectCurrentUser(state),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Profile)
