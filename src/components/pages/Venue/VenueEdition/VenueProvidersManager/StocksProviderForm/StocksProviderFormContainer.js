import { getRequestErrorStringFromErrors } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { showNotificationV1 } from 'store/reducers/notificationReducer'

import StocksProviderForm from './StocksProviderForm'

export const mapDispatchToProps = dispatch => ({
  createVenueProvider: (handleFail, handleSuccess, payload) => {
    dispatch(
      requestData({
        apiPath: `/venueProviders`,
        body: payload,
        handleFail: handleFail,
        handleSuccess: handleSuccess,
        method: 'POST',
      })
    )
  },
  notify: errors => {
    dispatch(
      showNotificationV1({
        text: getRequestErrorStringFromErrors(errors),
        type: 'danger',
      })
    )
  },
})

export default compose(withRouter, connect(null, mapDispatchToProps))(StocksProviderForm)
