import { StatusToggleButton } from 'components/pages/Offers/Offer/OfferStatus/StatusToggleButton'
import { connect } from 'react-redux'
import { showNotification } from 'store/reducers/notificationReducer'

const mapDispatchToProps = dispatch => ({
  notifySuccess: hasBeenActivated =>
    dispatch(
      showNotification({
        type: 'success',
        text: `L’offre a bien été ${
          hasBeenActivated ? 'activée' : 'désactivée'
        }.`,
      })
    ),
  notifyError: () =>
    dispatch(
      showNotification({
        type: 'error',
        text: 'Une erreur est survenue, veuillez réessayer ultérieurement.',
      })
    ),
})

export default connect(null, mapDispatchToProps)(StatusToggleButton)
