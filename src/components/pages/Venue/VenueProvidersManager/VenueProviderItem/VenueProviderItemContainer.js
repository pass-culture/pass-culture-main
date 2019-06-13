import { connect } from 'react-redux'

import VenueProviderItem from './VenueProviderItem'
import { selectEventsByProviderId } from '../../../../../selectors/selectEventsByProviderId'
import selectThingsByProviderId from '../../../../../selectors/selectThingsByProviderId'

export const mapStateToProps = (state, ownProps) => {
  const {
    venueProvider: { providerId },
  } = ownProps

  return {
    events: selectEventsByProviderId(state, providerId),
    things: selectThingsByProviderId(state, providerId),
  }
}

export default connect(mapStateToProps)(VenueProviderItem)
