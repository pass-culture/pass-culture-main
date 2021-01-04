import { connect } from 'react-redux'

import DeleteStockDialog from 'components/pages/Offer/Offer/Stocks/DeleteStockDialog/DeleteStockDialog'
import { showNotificationV2 } from 'store/reducers/notificationReducer'

const mapDispatchToProps = dispatch => ({
  notifyDeletionSuccess: () =>
    dispatch(
      showNotificationV2({
        type: 'success',
        text: 'Le stock a été supprimé.',
      })
    ),
  notifyDeletionError: () =>
    dispatch(
      showNotificationV2({
        type: 'error',
        text: 'Une erreur est survenue lors de la suppression du stock.',
      })
    ),
})

export default connect(null, mapDispatchToProps)(DeleteStockDialog)
