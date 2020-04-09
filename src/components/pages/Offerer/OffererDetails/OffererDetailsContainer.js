import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererDetails from './OffererDetails'
import { makeOffererComponentValueObject } from './OffererFactory'

import { withRequiredLogin } from '../../../hocs'
import withTracking from '../../../hocs/withTracking'
import { selectOffererById } from '../../../../selectors/data/offerersSelectors'
import { selectPhysicalVenuesByOffererId } from '../../../../selectors/data/venuesSelectors'
import { selectUserOffererByOffererIdAndUserIdAndRightsType } from '../../../../selectors/data/userOfferersSelectors'
import { requestData } from 'redux-saga-data'
import { offererNormalizer } from '../../../../utils/normalizers'

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
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(OffererDetails)
