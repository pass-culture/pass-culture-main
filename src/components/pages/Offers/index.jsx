import {
  lastTrackerMoment,
  withLogin,
  withPagination,
} from 'pass-culture-shared'

import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawOffers from './RawOffers'
import offersSelector from '../../../selectors/offers'
import offererSelector from '../../../selectors/offerer'
import venueSelector from '../../../selectors/venue'
import { mapApiToWindow, windowToApiQuery } from '../../../utils/pagination'

function mapStateToProps(state, ownProps) {
  const { offererId, venueId } = ownProps.pagination.apiQuery
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: offersSelector(state, offererId, venueId),
    offerer: offererSelector(state, offererId),
    user: state.user,
    types: state.data.types,
    venue: venueSelector(state, venueId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  withPagination({
    dataKey: 'offers',
    defaultWindowQuery: {
      [mapApiToWindow.offererId]: null,
      [mapApiToWindow.keywords]: null,
      [mapApiToWindow.venueId]: null,
      orderBy: 'offer.id+desc',
    },
    windowToApiQuery,
  }),
  withQueryRouter,
  connect(mapStateToProps)
)(RawOffers)
