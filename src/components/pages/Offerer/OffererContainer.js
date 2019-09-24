import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'

import { withRequiredLogin } from '../../hocs'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectOffererById from '../../../selectors/selectOffererById'
import selectPhysicalVenuesByOffererId from '../../../selectors/selectPhysicalVenuesByOffererId'
import get from 'lodash.get'
import { requestData } from 'redux-saga-data'
import { offererNormalizer } from '../../../utils/normalizers'
import { showNotification } from 'pass-culture-shared'
import withTracking from '../../hocs/withTracking'

export const mapStateToProps = (state, ownProps) => {
  const { currentUser, match } = ownProps
  const {
    params: { offererId },
  } = match
  const { id: currentUserId } = currentUser

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    ),
    offerer: selectOffererById(state, offererId),
    offererName: get(state, 'form.offerer.name'),
    venues: selectPhysicalVenuesByOffererId(state, offererId),
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    getOfferer: (offererId, handleFail, handleSuccess) => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          handleSuccess,
          handleFail,
          normalizer: offererNormalizer,
        })
      )
    },
    getUserOfferers: offererId => {
      dispatch(
        requestData({
          apiPath: `/userOfferers/${offererId}`,
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
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackCreateOffererSuccess: createdOffererId => {
      ownProps.tracking.trackEvent({ action: 'createOfferer', name: createdOffererId })
    }
  }
}

export default compose(
  withTracking('Offerer'),
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Offerer)
