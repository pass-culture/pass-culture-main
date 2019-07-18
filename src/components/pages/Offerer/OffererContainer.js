import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'

import { withRequiredLogin } from '../../hocs'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectOffererById from '../../../selectors/selectOffererById'
import selectPhysicalVenuesByOffererId from '../../../selectors/selectPhysicalVenuesByOffererId'
import get from 'lodash.get'

export const mapStateToProps = (state, ownProps) => {
  const { currentUser, match } = ownProps
  const {
    params: { offererId },
  } = match
  const { id: currentUserId } = currentUser || {}

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

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Offerer)
