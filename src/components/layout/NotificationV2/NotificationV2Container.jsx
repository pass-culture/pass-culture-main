import { connect } from 'react-redux'

import NotificationV2 from './NotificationV2'
import { notificationV2Selector } from 'store/selectors/notificationSelector'
import { closeNotification } from '../../../store/reducers/notificationReducer'

const mapStateToProps = state => ({
  notification: notificationV2Selector(state),
})

export const mapDispatchToProps = dispatch => ({
  hideNotification: () => {
    dispatch(closeNotification())
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(NotificationV2)
