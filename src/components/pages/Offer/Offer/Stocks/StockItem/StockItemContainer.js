import { connect } from 'react-redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'

import StockItem from './StockItem'

const mapDispatchToProps = dispatch => ({
  notifyUpdateError: () =>
    dispatch(
      showNotificationV2({
        type: 'error',
        text: 'Impossible de modifier le stock.',
      })
    ),
  notifyUpdateSuccess: () =>
    dispatch(
      showNotificationV2({
        type: 'success',
        text:
          'Le stock a bien été modifié. \n Si la date de l’évènement a été modifiée, les utilisateurs ayant déjà réservé cette offre seront prévenus par email.',
      })
    ),
})

export default connect(null, mapDispatchToProps)(StockItem)
