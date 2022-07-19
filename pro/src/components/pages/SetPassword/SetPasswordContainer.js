import { SetPassword } from './SetPassword'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/user/selectors'
import { showNotification } from 'store/reducers/notificationReducer'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  showNotification: (type, text) =>
    dispatch(
      showNotification({
        type: type,
        text: text,
      })
    ),
})

export default connect(mapStateToProps, mapDispatchToProps)(SetPassword)
