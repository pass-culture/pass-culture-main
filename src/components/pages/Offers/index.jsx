import { lastTrackerMoment } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RawOffers from './RawOffers'
import { withRequiredLogin } from '../../hocs'
import selectOffererById from '../../../selectors/selectOffererById'
import selectOffersByOffererIdAndVenueId from '../../../selectors/selectOffersByOffererIdAndVenueId'
import selectVenueById from '../../../selectors/selectVenueById'
import { translateQueryParamsToApiParams } from '../../../utils/translate'

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
  withRequiredLogin,
  connect(mapStateToProps)
)(RawOffers)
