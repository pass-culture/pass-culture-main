import { connect } from 'react-redux'
import Notification from './Notification'

function mapStateToProps(state) {
  return {
    notification: state.notification,
  }
}

export default connect(mapStateToProps)(Notification)
