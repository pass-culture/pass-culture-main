import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import VenueProvidersManager from './VenueProvidersManager'
import selectVenueProvidersByVenueId from './selectors/selectVenueProvidersByVenueId'
import { selectProviders } from '../../../../selectors/selectProviders'

export const mapStateToProps = (state, ownProps) => {
  const { venue } = ownProps
  const { id: venueId } = venue
  const providers = selectProviders(state)
  const venueProviders = selectVenueProvidersByVenueId(state, venueId)

  return {
    providers,
    venueProviders,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VenueProvidersManager)
