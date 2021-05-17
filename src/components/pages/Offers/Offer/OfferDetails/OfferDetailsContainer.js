import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { withTracking } from 'components/hocs'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser, selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import OfferDetails from './OfferDetails'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  userEmail: selectCurrentUser(state).email,
})

const mapDispatchToProps = dispatch => ({
  showErrorNotification: () =>
    dispatch(
      showNotification({
        type: 'error',
        text: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
      })
    ),
  showEditionSuccessNotification: () =>
    dispatch(
      showNotification({
        type: 'success',
        text: 'Votre offre a bien été modifiée',
      })
    ),
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackCreateOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'createOffer', name: offerId })
    },
    trackEditOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'modifyOffer', name: offerId })
    },
  }
}

export default compose(
  withTracking('Offer'),
  withRouter,
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(OfferDetails)
