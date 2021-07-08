import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import { showNotification } from 'store/reducers/notificationReducer'
import { offererNormalizer } from 'utils/normalizers'

import ApiKey from './ApiKey'

const mapDispatchToProps = dispatch => ({
  showNotification: (type, text) =>
    dispatch(
      showNotification({
        type,
        text,
      })
    ),
  loadOffererById: offererId => {
    dispatch(
      requestData({
        apiPath: `/offerers/${offererId}`,
        normalizer: offererNormalizer,
      })
    )
  },
})

export default connect(null, mapDispatchToProps)(ApiKey)
