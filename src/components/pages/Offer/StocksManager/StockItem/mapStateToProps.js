import selectFormInitialValuesByStockAndOfferIdAndOffererId from './selectFormInitialValuesByStockAndOfferIdAndOffererId'
import selectEventById from 'selectors/selectEventById'
import selectOfferById from 'selectors/selectOfferById'
import selectOffererById from 'selectors/selectOffererById'
import selectVenueById from 'selectors/selectVenueById'
import selectTimezoneByVenueId from 'selectors/selectTimezoneByVenueId'
import { translateQueryParamsToApiParams } from 'utils/translate'

export default function mapStateToProps(state, ownProps) {
  const {
    match: { params },
    query,
    stock,
  } = ownProps
  const { stockIdOrNew } = translateQueryParamsToApiParams(query.parse())

  const offerId = params.offerId
  const offer = selectOfferById(state, offerId)
  const { eventId, venueId } = offer || {}

  const event = selectEventById(state, eventId)

  const venue = selectVenueById(state, venueId)
  const managingOffererId = venue && venue.managingOffererId

  const stockPatch = selectFormInitialValuesByStockAndOfferIdAndOffererId(
    state,
    stock,
    offerId,
    managingOffererId
  )

  const offerer = selectOffererById(state, managingOffererId)
  const hasIban =
    (venue && typeof venue.iban !== 'undefined') ||
    (offerer && typeof offerer.iban !== 'undefined')

  const tz = selectTimezoneByVenueId(state, venueId)

  return {
    event,
    eventId,
    hasIban,
    offer,
    stockPatch,
    stockIdOrNew,
    tz,
    venue,
    venueId,
  }
}
