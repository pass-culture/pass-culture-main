import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OfferItem from './OfferItem'
import selectAggregatedStockByOfferId from 'selectors/selectAggregatedStockByOfferId'
import selectMaxDateByOfferId from 'selectors/selectMaxDateByOfferId'
import selectMediationsByOfferId from 'selectors/selectMediationsByOfferId'
import selectProductById from 'selectors/selectProductById'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import selectVenueById from 'selectors/selectVenueById'
import offererSelector from 'selectors/selectOffererById'
import { getOfferTypeLabel } from 'utils/offerItem'

function mapStateToProps(state, ownProps) {
  const { offer } = ownProps
  const { id: offerId, productId, venueId } = offer
  const product = selectProductById(state, productId)
  const venue = selectVenueById(state, venueId)
  const offerer = offererSelector(state, venue.managingOffererId)

  const stockAlertMessage = offer.stockAlertMessage

  return {
    aggregatedStock: selectAggregatedStockByOfferId(state, offerId),
    maxDate: selectMaxDateByOfferId(state, offerId),
    mediations: selectMediationsByOfferId(state, offerId),
    product,
    stocks: selectStocksByOfferId(state, offerId),
    offerer,
    offerTypeLabel: getOfferTypeLabel(product),
    stockAlertMessage,
    venue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(OfferItem)
