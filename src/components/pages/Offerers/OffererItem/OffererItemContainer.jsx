import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import selectPhysicalVenuesByOffererId from '../../../../selectors/selectPhysicalVenuesByOffererId'
import selectVenuesByOffererIdAndOfferType from '../../../../selectors/selectVenuesByOffererIdAndOfferType'

export const mapStateToProps = (state, ownProps) => {
  const {offerer: {id: offererId}} = ownProps
  return {
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererIdAndOfferType(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
