import { removeWhitespaces } from 'react-final-form-utils'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'


import { withRequiredLogin } from 'components/hocs'
import withTracking from 'components/hocs/withTracking'
import { closeNotification, showNotificationV1 } from 'store/reducers/notificationReducer'

import OffererCreation from './OffererCreation'

export const mapDispatchToProps = (dispatch, ownProps) => ({
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
      showNotificationV1({
        text: message,
        type: type,
      })
    )
  },
  closeNotification: () => {
    dispatch(closeNotification())
  },
  redirectToOfferersList: () => {
    ownProps.history.replace('/structures')
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
  }
}

export default compose(
  withTracking('Offerer'),
  withRequiredLogin,
  connect(null, mapDispatchToProps, mergeProps)
)(OffererCreation)
