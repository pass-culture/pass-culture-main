/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt deprecated "Gaël: deprecated usage of redux-saga-data"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

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
