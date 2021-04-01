import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

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
  showCreationSuccessNotification: () =>
    dispatch(
      showNotification({
        type: 'success',
        text: 'Votre offre a bien été créée',
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

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(OfferDetails)
