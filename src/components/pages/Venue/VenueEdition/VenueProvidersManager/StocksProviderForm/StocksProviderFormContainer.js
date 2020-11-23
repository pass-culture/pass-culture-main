import { connect } from 'react-redux'

import StocksProviderForm from 'components/pages/Venue/VenueEdition/VenueProvidersManager/StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from 'components/pages/Venue/VenueEdition/VenueProvidersManager/utils/getRequestErrorStringFromErrors'
import { showNotificationV1 } from 'store/reducers/notificationReducer'
import { fetchFromApiWithCredentials } from 'utils/fetch'

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
