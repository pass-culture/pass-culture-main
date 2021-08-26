/*
* @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { isFeatureActive } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import ThingStocks from './ThingStocks'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  areActivationCodesEnabled: isFeatureActive(state, 'ENABLE_ACTIVATION_CODES'),
  autoActivateDigitalBookings: isFeatureActive(state, 'AUTO_ACTIVATE_DIGITAL_BOOKINGS'),
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

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(ThingStocks)
