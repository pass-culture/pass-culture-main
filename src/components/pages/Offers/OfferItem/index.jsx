import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import RawOfferItem from './RawOfferItem'
import selectEventById from 'selectors/selectEventById'
import selectAggregatedStockByOfferId from 'selectors/selectAggregatedStockByOfferId'
import selectMaxDateByOfferId from 'selectors/selectMaxDateByOfferId'
import selectMediationsByOfferId from 'selectors/selectMediationsByOfferId'
import selectStocksByOfferId from 'selectors/selectStocksByOfferId'
import selectThingById from 'selectors/selectThingById'
import selectThumbUrlByOfferIdAndEventIdAndThingId from 'selectors/selectThumbUrlByOfferIdAndEventIdAndThingId'
import selectVenueById from 'selectors/selectVenueById'
import offererSelector from 'selectors/selectOffererById'
import { getOfferTypeLabel } from 'utils/offerItem'

function mapStateToProps(state, ownProps) {
  const { offer } = ownProps
  const { id: offerId, eventId, thingId, venueId } = offer
  const event = selectEventById(state, eventId)
  const thing = selectThingById(state, thingId)
  const venue = selectVenueById(state, venueId)
  const offerer = offererSelector(state, venue.managingOffererId)
  const stockAlertMessage = offer.stockAlertMessage

  return {
    aggregatedStock: selectAggregatedStockByOfferId(state, offerId),
    event,
    maxDate: selectMaxDateByOfferId(state, offerId),
    mediations: selectMediationsByOfferId(state, offerId),
    stocks: selectStocksByOfferId(state, offerId),
    thing,
    thumbUrl: selectThumbUrlByOfferIdAndEventIdAndThingId(
      state,
      offerId,
      eventId,
      thingId
    ),
    offerer,
    offerTypeLabel: getOfferTypeLabel(event, thing),
    stockAlertMessage,
    venue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawOfferItem)
