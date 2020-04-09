import { closeNotification, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import OffererCreation from './OffererCreation'

import { withRequiredLogin } from '../../../hocs'
import withTracking from '../../../hocs/withTracking'
import { removeWhitespaces } from 'react-final-form-utils'

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
      showNotification({
        text: message,
        type: type,
      })
    )
  },
  closeNotification: () => {
    dispatch(closeNotification())
  },
  redirectToOfferersList: () => {
    ownProps.history.push('/structures')
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
  connect(
    null,
    mapDispatchToProps,
    mergeProps
  )
)(OffererCreation)
