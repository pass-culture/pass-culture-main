import { connect } from 'react-redux'
import { compose } from 'redux'

import RawStocksManager from './RawStocksManager'
import { withFrenchQueryRouter } from 'components/hocs'
import selectEventById from 'selectors/selectEventById'
import selectOfferById from 'selectors/selectOfferById'
import selectProviderById from 'selectors/selectProviderById'
import selectThingById from 'selectors/selectThingById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'

function mapStateToProps(state, ownProps) {
  const {
    match: {
      params: { offerId },
    },
  } = ownProps

  const offer = selectOfferById(state, offerId)

  const { eventId, thingId } = offer
  const event = selectEventById(state, eventId)
  const thing = selectThingById(state, thingId)

  const stocks = selectStocksByOfferId(state, offerId)

  const isEventStock = typeof event !== 'undefined'

  const provider = selectProviderById(state, event && event.lastProviderId)

  return {
    event,
    isEventStock,
    offer,
    provider,
    stocks,
    thing,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawStocksManager)
