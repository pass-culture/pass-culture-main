import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import Stocks from './Stocks'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
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
  showSuccessNotification: () =>
    dispatch(
      showNotification({
        type: 'success',
        text: 'Vos stocks ont bien été sauvegardés.',
      })
    ),
  showSuccessNotificationStocksAndOffer: () =>
    dispatch(
      showNotification({
        type: 'success',
        text: 'Votre offre a bien été créée et vos stocks sauvegardés.',
      })
    ),
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(Stocks)
