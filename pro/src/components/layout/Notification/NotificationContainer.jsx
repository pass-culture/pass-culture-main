import Notification from 'components/layout/Notification/Notification'
import { closeNotification } from 'store/reducers/notificationReducer'
import { connect } from 'react-redux'
import { notificationSelector } from 'store/selectors/notificationSelector'

const mapStateToProps = state => ({
  notification: notificationSelector(state),
})

export const mapDispatchToProps = dispatch => ({
  hideNotification: () => {
    dispatch(closeNotification())
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(Notification)
