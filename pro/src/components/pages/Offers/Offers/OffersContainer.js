import { connect } from 'react-redux'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'

import Offers from './Offers'

export const mapDispatchToProps = dispatch => ({
  showInformationNotification: information =>
    dispatch(
      showNotification({
        type: 'information',
        text: information,
      })
    ),
})

export default compose(connect(null, mapDispatchToProps))(Offers)
