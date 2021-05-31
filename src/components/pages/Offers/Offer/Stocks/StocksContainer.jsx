import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from '../../../../../store/reducers/notificationReducer'
import { selectIsFeatureActive } from '../../../../../store/selectors/data/featuresSelectors'

import Stocks from './Stocks'

const mapStateToProps = state => ({
  areActivationCodesEnabled: selectIsFeatureActive(state, 'ENABLE_ACTIVATION_CODES'),
  autoActivateDigitalBookings: selectIsFeatureActive(state, 'AUTO_ACTIVATE_DIGITAL_BOOKINGS'),
})

const mapDispatchToProps = dispatch => ({
  showErrorNotification: () =>
    dispatch(
      showNotification({
        type: 'error',
        text: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
      })
    ),
  showSuccessNotification: text =>
    dispatch(
      showNotification({
        type: 'success',
        text,
      })
    ),
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(Stocks)
