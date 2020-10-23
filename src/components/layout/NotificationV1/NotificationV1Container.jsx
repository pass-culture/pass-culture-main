import { connect } from 'react-redux'

import NotificationV1 from 'components/layout/NotificationV1/NotificationV1'
import { notificationV1Selector } from 'store/selectors/notificationSelector'

const mapStateToProps = state => ({
  notification: notificationV1Selector(state),
})

export default connect(mapStateToProps)(NotificationV1)
