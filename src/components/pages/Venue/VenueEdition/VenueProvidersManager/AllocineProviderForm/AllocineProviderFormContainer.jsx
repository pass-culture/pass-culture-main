import { getRequestErrorStringFromErrors, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import AllocineProviderForm from './AllocineProviderForm'

export const mapDispatchToProps = (dispatch) => {
  return {
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
          type: 'fail',
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(AllocineProviderForm)
