import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { isFeatureActive } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import OffererCreation from './OffererCreation'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    isEntrepriseApiDisabled: isFeatureActive(state, 'DISABLE_ENTERPRISE_API'),
  }
}

export const mapDispatchToProps = dispatch => ({
  showNotification: (message, type) => {
    dispatch(
      showNotification({
        text: message,
        type: type,
      })
    )
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    redirectAfterSubmit: createdOffererId => {
      ownProps.history.replace(`/accueil?structure=${createdOffererId}`)
    },
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(OffererCreation)
