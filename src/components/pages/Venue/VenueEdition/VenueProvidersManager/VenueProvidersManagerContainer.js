import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import * as providersApi from 'repository/pcapi/providersApi'
import { selectProviders } from 'store/selectors/data/providersSelectors'
import { selectVenueProvidersByVenueId } from 'store/selectors/data/venueProvidersSelectors'

import VenueProvidersManager from './VenueProvidersManager'

export const mapStateToProps = (state, ownProps) => {
  const { venue } = ownProps
  const providers = selectProviders(state)
  const venueProviders = selectVenueProvidersByVenueId(state, venue.id)

  return {
    providers,
    venueProviders,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    loadProvidersAndVenueProviders: () => {
      const venueId = ownProps.venue.id
      providersApi.loadProviders(venueId).then(providers =>
        dispatch({
          type: 'SET_PROVIDERS',
          payload: providers,
        })
      )
      providersApi.loadVenueProviders(venueId).then(venueProviders =>
        dispatch({
          type: 'SET_VENUE_PROVIDERS',
          payload: venueProviders,
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(VenueProvidersManager)
