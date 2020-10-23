import { connect } from 'react-redux'

import NotificationV2 from 'components/layout/NotificationV2/NotificationV2'
import { closeNotification } from 'store/reducers/notificationReducer'
import { notificationV2Selector } from 'store/selectors/notificationSelector'

const mapStateToProps = state => ({
  notification: notificationV2Selector(state),
})

export const mapDispatchToProps = dispatch => ({
  hideNotification: () => {
    dispatch(closeNotification())
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(NotificationV2)
