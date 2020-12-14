import { connect } from 'react-redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'

import OfferForm from './OfferForm'

const mapDispatchToProps = dispatch => ({
  showErrorNotification: () =>
    dispatch(
      showNotificationV2({
        type: 'error',
        text: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
      })
    ),
})

export default connect(null, mapDispatchToProps)(OfferForm)
