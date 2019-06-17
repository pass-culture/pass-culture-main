import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import selectPhysicalVenuesByOffererId from '../../../selectors/selectPhysicalVenuesByOffererId'
import selectVenuesByOffererIdAndOfferType from '../../../selectors/selectVenuesByOffererIdAndOfferType'

export function mapStateToProps(state, ownProps) {
  const offererId = ownProps.offerer.id
  return {
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererIdAndOfferType(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
