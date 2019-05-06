import get from 'lodash.get'
import { selectCurrentUser } from 'with-login'

import selectProviderById from 'selectors/selectProviderById'
import selectProviders from 'selectors/selectProviders'
import selectVenueProviderByVenueIdAndVenueProviderId from './selectVenueProviderByVenueIdAndVenueProviderId'
import selectVenueProvidersByVenueId from './selectVenueProvidersByVenueId'

const mapStateToProps = (state, ownProps) => {
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
    currentUser: selectCurrentUser(state),
    provider,
    providers,
    venueProvider: selectVenueProviderByVenueIdAndVenueProviderId(
      state,
      venueId
    ),
    venueProviders: selectVenueProvidersByVenueId(state, venueId),
  }
}

export default mapStateToProps
