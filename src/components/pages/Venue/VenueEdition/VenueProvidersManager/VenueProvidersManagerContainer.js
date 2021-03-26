import { connect } from 'react-redux'

import { showNotificationV1 } from 'store/reducers/notificationReducer'

import { getRequestErrorStringFromErrors } from './utils/getRequestErrorStringFromErrors'
import VenueProvidersManager from './VenueProvidersManager'

const mapDispatchToProps = dispatch => ({
  notify: errors => {
    dispatch(
      showNotificationV1({
        text: getRequestErrorStringFromErrors(errors),
        type: 'danger',
      })
    )
  },
})

export default connect(null, mapDispatchToProps)(VenueProvidersManager)
