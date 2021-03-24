import { connect } from 'react-redux'

import StocksProviderForm from 'components/pages/Venue/VenueEdition/VenueProvidersManager/StocksProviderForm/StocksProviderForm'
import { getRequestErrorStringFromErrors } from 'components/pages/Venue/VenueEdition/VenueProvidersManager/utils/getRequestErrorStringFromErrors'
import * as providersApi from 'repository/pcapi/providersApi'
import { showNotificationV1 } from 'store/reducers/notificationReducer'

const mapDispatchToProps = dispatch => ({
  createVenueProvider: payload =>
    providersApi.createVenueProvider(payload).then(venueProvider => {
      dispatch({
        type: 'SET_VENUE_PROVIDERS',
        payload: [venueProvider],
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
