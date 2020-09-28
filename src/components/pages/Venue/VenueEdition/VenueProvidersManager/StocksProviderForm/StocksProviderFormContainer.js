import { getRequestErrorStringFromErrors, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
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
      showNotification({
        text: getRequestErrorStringFromErrors(errors),
        type: 'danger',
      })
    )
  },
})

export default compose(withRouter, connect(null, mapDispatchToProps))(StocksProviderForm)
