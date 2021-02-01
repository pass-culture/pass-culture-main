import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { SetPassword } from './SetPassword'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  showNotification: (type, text) =>
    dispatch(
      showNotificationV2({
        type: type,
        text: text,
      })
    ),
})

export default compose(connect(mapStateToProps, mapDispatchToProps))(withRouter(SetPassword))
