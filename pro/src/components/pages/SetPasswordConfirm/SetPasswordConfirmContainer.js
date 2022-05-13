import { SetPasswordConfirm } from './SetPasswordConfirm'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default connect(mapStateToProps)(SetPasswordConfirm)
