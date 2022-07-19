import { SetPasswordConfirm } from './SetPasswordConfirm'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/user/selectors'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(SetPasswordConfirm)
