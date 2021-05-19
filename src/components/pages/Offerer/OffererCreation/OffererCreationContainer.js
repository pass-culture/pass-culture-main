import { removeWhitespaces } from 'react-final-form-utils'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import withTracking from 'components/hocs/withTracking'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import OffererCreation from './OffererCreation'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  createNewOfferer: (payload, onHandleFail, onHandleSuccess) => {
    const { siren } = payload
    dispatch(
      requestData({
        apiPath: `/offerers`,
        method: 'POST',
        body: { ...payload, siren: removeWhitespaces(siren) },
        handleFail: onHandleFail,
        handleSuccess: onHandleSuccess,
      })
    )
  },
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
    trackCreateOfferer: createdOffererId => {
      ownProps.tracking.trackEvent({ action: 'createOfferer', name: createdOffererId })
    },
    redirectAfterSubmit: createdOffererId => {
      ownProps.history.replace(`/accueil?structure=${createdOffererId}`)
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offerer'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(OffererCreation)
