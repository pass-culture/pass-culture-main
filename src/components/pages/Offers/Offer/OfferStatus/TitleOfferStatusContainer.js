import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { TitleOfferStatus } from 'components/pages/Offers/Offer/OfferStatus/TitleOfferStatus'
import { showNotification } from 'store/reducers/notificationReducer'

const mapDispatchToProps = dispatch => ({
  notifySuccessfulOfferActivationStatusToggle: hasBeenActivated =>
    dispatch(
      showNotification({
        type: 'success',
        text: `L’offre a bien été ${hasBeenActivated ? 'activée' : 'désactivée'}.`,
      })
    ),
})

export default compose(withRouter, connect(null, mapDispatchToProps))(TitleOfferStatus)
