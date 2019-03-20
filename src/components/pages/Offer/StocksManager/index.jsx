import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawStocksManager from './RawStocksManager'
import selectEventById from 'selectors/selectEventById'
import selectOfferById from 'selectors/selectOfferById'
import selectProviderById from 'selectors/selectProviderById'
import selectThingById from 'selectors/selectThingById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import selectStockErrorsByStockId from 'selectors/selectStockErrorsByStockId'
import { translateQueryParamsToApiParams } from 'utils/translate'

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { offerId },
    },
    query,
  } = ownProps
  const apiParams = translateQueryParamsToApiParams(query.parse())
  const { stockIdOrNew } = apiParams

  const offer = selectOfferById(state, offerId)

  const { eventId, thingId } = offer
  const event = selectEventById(state, eventId)
  const thing = selectThingById(state, thingId)

  const stocks = selectStocksByOfferId(state, offerId)
  const errors = selectStockErrorsByStockId(state, stockIdOrNew)

  const isEventStock = typeof event !== 'undefined'

  const provider = selectProviderById(state, event && event.lastProviderId)

  return {
    errors,
    event,
    isEventStock,
    offer,
    provider,
    stockIdOrNew,
    stocks,
    thing,
  }
}

export default compose(
  withQueryRouter,
  connect(mapStateToProps)
)(RawStocksManager)
