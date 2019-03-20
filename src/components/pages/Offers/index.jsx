import { lastTrackerMoment } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawOffers from './RawOffers'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'
import selectOffererById from 'selectors/selectOffererById'
import selectOffersByOffererIdAndVenueId from 'selectors/selectOffersByOffererIdAndVenueId'
import selectVenueById from 'selectors/selectVenueById'
import { translateQueryParamsToApiParams } from 'utils/translate'

export function mapStateToProps(state, ownProps) {
  const { query } = ownProps
  const queryParams = query.parse()
  const apiQueryParams = translateQueryParamsToApiParams(queryParams)
  const { offererId, venueId } = apiQueryParams
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: selectOffersByOffererIdAndVenueId(state, offererId, venueId),
    offerer: selectOffererById(state, offererId),
    types: state.data.types,
    venue: selectVenueById(state, venueId),
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withQueryRouter,
  connect(mapStateToProps)
)(RawOffers)
