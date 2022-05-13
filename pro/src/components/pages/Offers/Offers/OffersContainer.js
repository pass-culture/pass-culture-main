import Offers from './Offers'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { showNotification } from 'store/reducers/notificationReducer'

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
