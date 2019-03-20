import selectStockPatchByStockAndOfferIdAndOffererId from './selectStockPatchByStockAndOfferIdAndOffererId'
import selectEventById from 'selectors/selectEventById'
import selectOfferById from 'selectors/selectOfferById'
import selectOffererById from 'selectors/selectOffererById'
import selectVenueById from 'selectors/selectVenueById'
import timezoneSelector from 'selectors/timezone'
import { translateQueryParamsToApiParams } from 'utils/translate'

export default function mapStateToProps(state, ownProps) {
  const { form } = state
  const {
    match: { params },
    query,
    stock,
  } = ownProps
  const { id: stockId } = stock || {}
  const { stockIdOrNew } = translateQueryParamsToApiParams(query.parse())

  const offerId = params.offerId
  const offer = selectOfferById(state, offerId)
  const { eventId, venueId } = offer || {}

  const venue = selectVenueById(state, venueId)
  const managingOffererId = venue && venue.managingOffererId

  const stockPatch = selectStockPatchByStockAndOfferIdAndOffererId(
    state,
    stock,
    offerId,
    managingOffererId
  )

  const isReadOnly =
    !stockIdOrNew ||
    (stockIdOrNew === 'nouveau' && typeof stockId !== 'undefined') ||
    (stockIdOrNew !== 'nouveau' && stockId !== stockIdOrNew)

  const offerer = selectOffererById(state, managingOffererId)
  const hasIban =
    (venue && typeof venue.iban !== 'undefined') ||
    (offerer && typeof offerer.iban !== 'undefined')

  const stockFormKey = (stockPatch && stockPatch.id) || ''
  const stockForm = form && form[`stock${stockFormKey}`]
  const {
    beginningDatetime: formBeginningDatetime,
    bookingLimitDatetime: formBookingLimitDatetime,
    endDatetime: formEndDatetime,
    price: formPrice,
  } =
    stockForm || {}

  return {
    event: selectEventById(state, eventId),
    eventId,
    formBeginningDatetime,
    formBookingLimitDatetime,
    formEndDatetime,
    formPrice,
    hasIban,
    isReadOnly,
    offer,
    stockFormKey,
    stockPatch,
    stockIdOrNew,
    tz: timezoneSelector(state, venueId),
    venue,
    venueId,
  }
}
