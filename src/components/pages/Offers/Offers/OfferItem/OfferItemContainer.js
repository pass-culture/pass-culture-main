import { connect } from 'react-redux'
import { compose } from 'redux'

import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'

import OfferItem from './OfferItem'

export const mapStateToProps = (state, ownProps) => {
  const { offer } = ownProps
  const { id: offerId, venueId } = offer
  const venue = selectVenueById(state, venueId)

  return {
    stocks: selectStocksByOfferId(state, offerId),
    venue,
  }
}

export default compose(connect(mapStateToProps))(OfferItem)
