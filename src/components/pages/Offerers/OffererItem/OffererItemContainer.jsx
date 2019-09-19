import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import {
  selectPhysicalVenuesByOffererId,
  selectVenuesByOffererId,
} from '../../../../selectors/data/venuesSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    offerer: { id: offererId },
  } = ownProps
  return {
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererId(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
