import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import VenueProvidersManager from './VenueProvidersManager'
import get from 'lodash.get'
import selectVenueProviderByVenueIdAndVenueProviderId from './selectors/selectVenueProviderByVenueIdAndVenueProviderId'
import selectVenueProvidersByVenueId from './selectors/selectVenueProvidersByVenueId'
import { selectProviders } from '../../../../selectors/selectProviders'
import { selectProviderById } from '../../../../selectors/selectProviderById'

export const mapStateToProps = (state, ownProps) => {
  const { venue } = ownProps
  const { id: venueId } = venue || {}
  const providers = selectProviders(state)
  const formPatch = get(state, 'form.venueProvider')

  let provider
  if (providers.length === 1) {
    provider = providers[0]
  } else {
    const providerId = get(formPatch, 'providerId')
    provider = selectProviderById(state, providerId)
  }

  return {
    provider,
    providers,
    venueProvider: selectVenueProviderByVenueIdAndVenueProviderId(
      state,
      venueId
    ),
    venueProviders: selectVenueProvidersByVenueId(state, venueId),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VenueProvidersManager)
