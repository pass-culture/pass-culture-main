import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withRequiredLogin } from 'components/hocs'
import withTracking from 'components/hocs/withTracking'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectUserOffererByOffererIdAndUserIdAndRightsType } from 'store/selectors/data/userOfferersSelectors'
import { selectPhysicalVenuesByOffererId } from 'store/selectors/data/venuesSelectors'


import { offererNormalizer } from '../../../../utils/normalizers'

import OffererDetails from './OffererDetails'
import { makeOffererComponentValueObject } from './OffererFactory'

export const mapStateToProps = (state, ownProps) => {
  const { currentUser, match } = ownProps
  const {
    params: { offererId },
  } = match
  const { id: currentUserId } = currentUser

  return {
    offerer: makeOffererComponentValueObject(
      selectUserOffererByOffererIdAndUserIdAndRightsType,
      selectOffererById,
      offererId,
      currentUserId,
      state
    ),
    offererId,
    venues: selectPhysicalVenuesByOffererId(state, offererId),
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    loadOffererById: offererId => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          normalizer: offererNormalizer,
        })
      )
    },
  }
}

export default compose(
  withTracking('Offerer'),
  withRequiredLogin,
  connect(mapStateToProps, mapDispatchToProps)
)(OffererDetails)
