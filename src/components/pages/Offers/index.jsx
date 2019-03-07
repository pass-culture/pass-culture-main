import { lastTrackerMoment, withLogin } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawOffers from './RawOffers'
import offersSelector from '../../../selectors/offers'
import offererSelector from '../../../selectors/offerer'
import venueSelector from '../../../selectors/venue'
import { translateBrowserUrlToApiUrl } from '../../../utils/translate'

export function mapStateToProps(state, ownProps) {
  const { query } = ownProps
  const queryParams = query.parse()
  const { offererId, venueId } = translateBrowserUrlToApiUrl(queryParams)
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: offersSelector(state, offererId, venueId),
    offerer: offererSelector(state, offererId),
    types: state.data.types,
    venue: venueSelector(state, venueId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withQueryRouter,
  connect(mapStateToProps)
)(RawOffers)
