/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

import { getRequestErrorStringFromErrors } from './utils/getRequestErrorStringFromErrors'
import VenueProvidersManager from './VenueProvidersManager'

const mapDispatchToProps = dispatch => ({
  notifyError: errors => {
    dispatch(
      showNotification({
        text: getRequestErrorStringFromErrors(errors),
        type: 'error',
      })
    )
  },
  notifySuccess: () => {
    dispatch(
      showNotification({
        text: 'La synchronisation a bien été initiée.',
        type: 'success',
      })
    )
  },
})

export default connect(null, mapDispatchToProps)(VenueProvidersManager)
