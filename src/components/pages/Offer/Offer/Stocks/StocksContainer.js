import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'
import { selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import Stocks from './Stocks'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
})

const mapDispatchToProps = dispatch => ({
  showErrorNotification: () =>
    dispatch(
      showNotificationV2({
        type: 'error',
        text: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
      })
    ),
  showSuccessNotification: () =>
    dispatch(
      showNotificationV2({
        type: 'success',
        text: 'Vos stocks ont bien été sauvegardés.',
      })
    ),
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(Stocks)
