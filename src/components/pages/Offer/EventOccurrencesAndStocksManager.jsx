import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import eventSelector from '../../../selectors/event'
import eventOccurrencesSelector from '../../../selectors/eventOccurrences'
import eventOccurrenceAndStocksErrorsSelector from '../../../selectors/eventOccurrenceAndStockErrors'
import offerSelector from '../../../selectors/offer'
import thingSelector from '../../../selectors/thing'
import providerSelector from '../../../selectors/provider'
import selectApiSearch from '../../../selectors/selectApiSearch'
import stocksSelector from '../../../selectors/stocks'
import RawEventOccurrencesAndStocksManager from './RawEventOccurrencesAndStocksManager'

function mapStateToProps(state, ownProps) {
  const search = selectApiSearch(state, ownProps.location.search)
  const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}

  const editedStockId = eventOccurrenceIdOrNew || stockIdOrNew

  const isNew =
    eventOccurrenceIdOrNew === 'nouvelle' ||
    (!eventOccurrenceIdOrNew && stockIdOrNew === 'nouveau')

  const offerId = ownProps.match.params.offerId
  const offer = offerSelector(state, offerId)

  const eventId = get(offer, 'eventId')
  const event = eventSelector(state, eventId)
  const eventOccurrences = eventOccurrencesSelector(
    state,
    ownProps.match.params.offerId
  )

  const thingId = get(offer, 'thingId')
  const thing = thingSelector(state, thingId)

  const stocks = stocksSelector(state, offerId, event && eventOccurrences)

  const errors = eventOccurrenceAndStocksErrorsSelector(
    state,
    eventOccurrenceIdOrNew,
    stockIdOrNew
  )
  const isStockOnly = typeof get(thing, 'id') !== 'undefined'

  return {
    errors,
    event,
    eventOccurrenceIdOrNew,
    eventOccurrences,
    editedStockId,
    isNew,
    offer,
    provider: providerSelector(state, get(event, 'lastProviderId')),
    stocks,
    thing,
    isStockOnly,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawEventOccurrencesAndStocksManager)
