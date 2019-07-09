import {
  getRequestErrorStringFromErrors,
  showNotification,
} from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import VenueProvidersManager from './VenueProvidersManager'
import selectVenueProviderByVenueIdAndVenueProviderId from './selectors/selectVenueProviderByVenueIdAndVenueProviderId'
import selectVenueProvidersByVenueId from './selectors/selectVenueProvidersByVenueId'
import selectProviders from '../../../../selectors/selectProviders'

export const mapStateToProps = (state, ownProps) => {
  const { venue } = ownProps
  const { id: venueId } = venue
  const providers = selectProviders(state)
  const venueProviders = selectVenueProvidersByVenueId(state, venueId)

  return {
    providers,
    venueProviders,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
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
    loadProvidersAndVenueProviders: () => {
      const {
        match: {
          params: { venueId },
        },
      } = ownProps

      dispatch(
        requestData({
          apiPath: '/providers',
        })
      )
      dispatch(
        requestData({
          apiPath: `/venueProviders?venueId=${venueId}`,
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
    mapStateToProps,
    mapDispatchToProps
  )
)(VenueProvidersManager)
