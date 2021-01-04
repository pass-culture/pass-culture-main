import { connect } from 'react-redux'

import { showNotificationV2 } from 'store/reducers/notificationReducer'

import StockItem from './StockItem'

const mapDispatchToProps = dispatch => ({
  notifyCreateSuccess: () =>
    dispatch(
      showNotificationV2({
        type: 'success',
        text: 'Le stock a bien été ajouté.',
      })
    ),
  notifyError: errors => {
    return dispatch(
      showNotificationV2({
        type: 'error',
        text: errors.join('\n'),
      })
    )
  },
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
