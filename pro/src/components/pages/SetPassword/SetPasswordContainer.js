import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/user/selectors'

import { SetPassword } from './SetPassword'

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
