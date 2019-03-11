import get from 'lodash.get'
import eventSelector from '../../../../selectors/event'
import eventOccurrencePatchSelector from '../../../../selectors/eventOccurrencePatch'
import eventOccurrencesSelector from '../../../../selectors/eventOccurrences'
import offerSelector from '../../../../selectors/offer'
import offererSelector from '../../../../selectors/offerer'
import selectApiSearch from '../../../../selectors/selectApiSearch'
import stockSelector from '../../../../selectors/stock'
import stockPatchSelector from '../../../../selectors/stockPatch'
import timezoneSelector from '../../../../selectors/timezone'
import venueSelector from '../../../../selectors/venue'

export default function mapStateToProps(state, ownProps) {
  const search = selectApiSearch(state, ownProps.location.search)
  const { eventOccurrenceIdOrNew, stockIdOrNew } = search || {}

  const offerId = ownProps.match.params.offerId
  const offer = offerSelector(state, offerId)
  const { eventId, venueId } = offer || {}

  const eventOccurrencePatch = eventOccurrencePatchSelector(
    state,
    ownProps.eventOccurrence,
    ownProps.match.params.offerId,
    venueId
  )
  const eventOccurrenceId = get(eventOccurrencePatch, 'id')

  const isEventOccurrenceReadOnly =
    !eventOccurrenceIdOrNew ||
    (eventOccurrenceIdOrNew === 'nouvelle' && eventOccurrenceId) ||
    (eventOccurrenceIdOrNew !== 'nouvelle' &&
      eventOccurrenceId !== eventOccurrenceIdOrNew) ||
    stockIdOrNew ||
    !ownProps.isFullyEditable

  const venue = venueSelector(state, venueId)

  const stock = ownProps.isStockOnly
    ? ownProps.stock
    : stockSelector(state, offerId, get(ownProps, 'eventOccurrence'))

  const stockPatch = stockPatchSelector(
    state,
    stock,
    offerId,
    get(ownProps, 'eventOccurrence.id'),
    get(venue, 'managingOffererId')
  )

  const stockId = get(stock, 'id')

  const isStockReadOnly =
    (!ownProps.isStockOnly &&
      (!eventOccurrenceId ||
        !eventOccurrenceIdOrNew ||
        eventOccurrenceIdOrNew === 'nouvelle' ||
        eventOccurrenceIdOrNew !== eventOccurrenceId)) ||
    !stockIdOrNew ||
    (stockIdOrNew === 'nouveau' && stockId) ||
    (stockIdOrNew !== 'nouveau' && stockId !== stockIdOrNew)

  const isEditing = !isEventOccurrenceReadOnly || !isStockReadOnly

  const offerer = offererSelector(state, venue && venue.managingOffererId)
  const hasIban = (venue && venue.iban) || (offerer && offerer.iban)

  const stockFormKey = ownProps.isStockOnly
    ? (stockPatch && stockPatch.id) || ''
    : stockPatch && stockPatch.eventOccurrenceId

  return {
    event: eventSelector(state, eventId),
    eventId,
    eventOccurrencePatch,
    eventOccurrences: eventOccurrencesSelector(state, offerId),
    eventOccurrenceIdOrNew,
    formBeginningDatetime: get(
      state,
      `form.eventOccurrence${eventOccurrenceId || ''}.beginningDatetime`
    ),
    formBookingLimitDatetime: get(
      state,
      `form.stock${stockFormKey}.bookingLimitDatetime`
    ),
    formEndDatetime: get(
      state,
      `form.eventOccurrence${eventOccurrenceId || ''}.endDatetime`
    ),
    formPrice: get(state, `form.stock${stockFormKey}.price`),
    hasIban,
    isEditing,
    isEventOccurrenceReadOnly,
    isStockReadOnly,
    offer,
    stockFormKey,
    stockPatch,
    stockIdOrNew,
    tz: timezoneSelector(state, venueId),
    venue,
    venueId,
  }
}
