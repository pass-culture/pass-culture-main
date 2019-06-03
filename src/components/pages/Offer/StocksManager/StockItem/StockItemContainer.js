import { connect } from 'react-redux'
import { compose } from 'redux'

import StockItem from './StockItem'
import { withFrenchQueryRouter } from 'components/hocs'
import selectFormInitialValuesByStockAndOfferIdAndOffererIdAndTimezone
  from './selectors/selectFormInitialValuesByStockAndOfferIdAndOffererId'
import { translateQueryParamsToApiParams } from '../../../../../utils/translate'
import { selectOfferById } from '../../../../../selectors/selectOfferById'
import { selectProductById } from '../../../../../selectors/selectProductById'
import { selectVenueById } from '../../../../../selectors/selectVenueById'
import { selectOffererById } from '../../../../../selectors/selectOffererById'
import { selectTimezoneByVenueIdAndOffererId } from '../../../../../selectors/selectTimezoneByVenueIdAndOffererId'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: { params },
    query,
    stock,
  } = ownProps
  const { stockIdOrNew } = translateQueryParamsToApiParams(query.parse())

  const offerId = params.offerId
  const offer = selectOfferById(state, offerId)
  const { productId, venueId } = offer || {}

  const product = selectProductById(state, productId)

  const venue = selectVenueById(state, venueId)
  const managingOffererId = venue && venue.managingOffererId

  const offerer = selectOffererById(state, managingOffererId)
  const hasIban =
    (venue && typeof venue.iban !== 'undefined') ||
    (offerer && typeof offerer.iban !== 'undefined')

  const timezone = selectTimezoneByVenueIdAndOffererId(
    state,
    venueId,
    managingOffererId
  )

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
    product,
    productId,
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
