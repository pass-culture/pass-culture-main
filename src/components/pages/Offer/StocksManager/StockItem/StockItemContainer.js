import createCachedSelector from 're-reselect'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import withFrenchQueryRouter from 'components/hocs/withFrenchQueryRouter'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectOfferById } from 'store/selectors/data/offersSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'

import { getTimezone } from '../../../../../utils/timezone'
import { translateQueryParamsToApiParams } from '../../../../../utils/translate'
import Offer from '../ValueObjects/Offer'

import selectFormInitialValuesByStockAndOfferIdAndOffererIdAndTimezone from './selectors/selectFormInitialValuesByStockAndOfferIdAndOffererId'
import StockItem from './StockItem'

export const selectTimezoneByVenueIdAndOffererId = createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => selectOffererById(state, offererId),
  (venue, offerer) => {
    if (!venue) return

    if (!venue.isVirtual) return getTimezone(venue.departementCode)

    if (!offerer) return

    return getTimezone(offerer.postalCode.slice(0, 3))
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
  const associatedOffer = selectOfferById(state, offerId)
  const { venueId } = associatedOffer || {}

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

  const offer = new Offer(associatedOffer)

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

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    updateStockInformations: (stockId, body, handleSuccess, handleFail) => {
      const { query } = ownProps
      const context = query.context({ id: stockId, key: 'stock' })
      const { method } = context
      dispatch(
        requestData({
          apiPath: `/stocks/${stockId || ''}`,
          body,
          handleSuccess: handleSuccess,
          handleFail: handleFail,
          method,
        })
      )
    },

    deleteStock: (stockId, handleFail) => {
      dispatch(
        requestData({
          apiPath: `stocks/${stockId}`,
          handleFail: handleFail,
          method: 'DELETE',
        })
      )
    },
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(StockItem)
