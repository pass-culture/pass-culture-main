import { getRequestErrorStringFromErrors, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import FnacProviderForm from './FnacProviderForm'

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    createVenueProvider: (handleFail, handleSuccess) => {
      const { providerId, venueId, venueSiret } = ownProps
      const payload = {
        providerId: providerId,
        venueIdAtOfferProvider: venueSiret,
        venueId: venueId,
      }
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
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(FnacProviderForm)
