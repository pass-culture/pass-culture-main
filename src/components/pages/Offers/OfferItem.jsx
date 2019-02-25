import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import RawOfferItem from './RawOfferItem'

import aggregatedStockSelector from '../../../selectors/aggregatedStock'
import eventSelector from '../../../selectors/event'
import maxDateSelector from '../../../selectors/maxDate'
import mediationsSelector from '../../../selectors/mediations'
import eventOccurrencesSelector from '../../../selectors/eventOccurrences'
import stocksSelector from '../../../selectors/stocks'
import thingSelector from '../../../selectors/thing'
import thumbUrlSelector from '../../../selectors/thumbUrl'
import venueSelector from '../../../selectors/venue'
import offerrerSelector from '../../../selectors/offerer'

import { getOfferTypeLabel } from '../../../utils/offerItem'

function mapStateToProps(state, ownProps) {
  const { id, eventId, thingId } = ownProps.offer
  const event = eventSelector(state, eventId)
  const thing = thingSelector(state, thingId)
  const eventOccurrences = eventOccurrencesSelector(state, id)
  const venue = venueSelector(state, ownProps.offer.venueId)
  const offerrer = offerrerSelector(state, venue.managingOffererId)
  return {
    aggregatedStock: aggregatedStockSelector(
      state,
      id,
      event && eventOccurrences
    ),
    event,
    eventOccurrences,
    maxDate: maxDateSelector(state, id),
    mediations: mediationsSelector(state, id),
    stocks: stocksSelector(state, id, event && eventOccurrences),
    thing,
    thumbUrl: thumbUrlSelector(state, id, eventId, thingId),
    offerTypeLabel: getOfferTypeLabel(event, thing),
    venue,
    offerrer,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawOfferItem)
