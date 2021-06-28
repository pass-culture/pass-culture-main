import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

import ApiKey from './ApiKey'

const mapDispatchToProps = dispatch => ({
  showNotification: (type, text) =>
    dispatch(
      showNotification({
        type,
        text,
      })
    ),
})

export default connect(null, mapDispatchToProps)(ApiKey)
