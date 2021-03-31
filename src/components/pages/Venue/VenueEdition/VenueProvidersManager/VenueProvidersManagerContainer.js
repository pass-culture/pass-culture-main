import { connect } from 'react-redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'

import { getRequestErrorStringFromErrors } from './utils/getRequestErrorStringFromErrors'
import VenueProvidersManager from './VenueProvidersManager'

const mapDispatchToProps = dispatch => ({
  notifyError: errors => {
    dispatch(
      showNotificationV2({
        text: getRequestErrorStringFromErrors(errors),
        type: 'error',
      })
    )
  },
  notifySuccess: () => {
    dispatch(
      showNotificationV2({
        text: 'La synchronisation a bien été initiée.',
        type: 'success',
      })
    )
  },
})

export default connect(null, mapDispatchToProps)(VenueProvidersManager)
