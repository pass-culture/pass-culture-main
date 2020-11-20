import { connect } from 'react-redux'

import { showNotificationV1 } from 'store/reducers/notificationReducer'
import { fetchFromApiWithCredentials } from 'utils/fetch'

import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'

import StocksProviderForm from './StocksProviderForm'

const mapDispatchToProps = dispatch => ({
  createVenueProvider: payload =>
    fetchFromApiWithCredentials('/venueProviders', 'POST', payload).then(venueProvider => {
      dispatch({
        type: 'SET_VENUE_PROVIDERS',
        payload: venueProvider,
      })

      return venueProvider
    }),
  notify: errors => {
    dispatch(
      showNotificationV1({
        text: getRequestErrorStringFromErrors(errors),
        type: 'danger',
      })
    )
  },
})

export default connect(null, mapDispatchToProps)(StocksProviderForm)
