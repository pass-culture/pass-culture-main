import createCachedSelector from 're-reselect'
import { connect } from 'react-redux'
import { compose } from 'redux'

import StockItem from './StockItem'
import withFrenchQueryRouter from '../../../../hocs/withFrenchQueryRouter'
import selectFormInitialValuesByStockAndOfferIdAndOffererIdAndTimezone from './selectors/selectFormInitialValuesByStockAndOfferIdAndOffererId'
import { translateQueryParamsToApiParams } from '../../../../../utils/translate'
import { selectVenueById } from '../../../../../selectors/data/venuesSelectors'
import { selectOffererById } from '../../../../../selectors/data/offerersSelectors'
import { selectOfferById } from '../../../../../selectors/data/offersSelectors'

const getTimezoneFromDepartementCode = departementCode => {
  switch (departementCode) {
    case '97':
    case '973':
      return 'America/Cayenne'
    default:
      return 'Europe/Paris'
  }
}

export const selectTimezoneByVenueIdAndOffererId = createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => selectOffererById(state, offererId),
  (venue, offerer) => {
    if (!venue) return

    if (!venue.isVirtual) return getTimezoneFromDepartementCode(venue.departementCode)

    if (!offerer) return

    return getTimezoneFromDepartementCode(offerer.postalCode.slice(0, 2))
  }
)((state, venueId = '', offererId = '') => `${venueId}${offererId}`)

export const mapStateToProps = (state, ownProps) => {
  const {
    match: { params },
    query,
    stock,
  } = ownProps
  const { stockIdOrNew } = translateQueryParamsToApiParams(query.parse())

  const offerId = params.offerId
  const offer = selectOfferById(state, offerId)
  const { venueId } = offer || {}

  const venue = selectVenueById(state, venueId)
  const managingOffererId = venue && venue.managingOffererId

  const offerer = selectOffererById(state, managingOffererId)
  const hasIban =
    (venue && typeof venue.iban !== 'undefined') || (offerer && typeof offerer.iban !== 'undefined')

  const timezone = selectTimezoneByVenueIdAndOffererId(state, venueId, managingOffererId)

  const stockPatch = selectFormInitialValuesByStockAndOfferIdAndOffererIdAndTimezone(
    state,
    stock,
    offerId,
    managingOffererId,
    timezone
  )

  return {
    hasIban,
    offer,
    stockPatch,
    stockIdOrNew,
    timezone,
    venue,
    venueId,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StockItem)
