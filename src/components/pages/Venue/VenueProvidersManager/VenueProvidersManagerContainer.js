import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import VenueProvidersManager from './VenueProvidersManager'
import selectVenueProvidersByVenueId from './selectors/selectVenueProvidersByVenueId'
import { selectProviders } from '../../../../selectors/data/providersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { venue } = ownProps
  const { id: venueId, siret: venueSiret } = venue
  const providers = selectProviders(state)
  const venueProviders = selectVenueProvidersByVenueId(state, venueId)

  return {
    providers,
    venueProviders,
    venueSiret
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    loadProvidersAndVenueProviders: () => {
      const {
        match: {
          params: { venueId },
        },
      } = ownProps
      dispatch(
        requestData({
          apiPath: `/providers/${venueId}`,
        })
      )
      dispatch(
        requestData({
          apiPath: `/venueProviders?venueId=${venueId}`,
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(VenueProvidersManager)
