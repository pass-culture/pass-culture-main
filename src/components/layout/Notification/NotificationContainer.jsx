import { connect } from 'react-redux'

import Notification from './Notification'

const mapStateToProps = state => ({
  notification: state.notification,
})

export default connect(mapStateToProps)(Notification)
