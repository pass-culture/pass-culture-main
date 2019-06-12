import {compose} from "redux"
import {connect} from "react-redux"
import { withFrenchQueryRouter } from 'components/hocs'

import StockItem from "../Offer/StocksManager/StockItem/StockItem"
import selectOffersByVenueId from "../../../selectors/selectOffersByVenueId"

export const mapStateToProps = (state, ownProps) => {
  const venueId = "AM"
  const offers = selectOffersByVenueId(state, venueId)

  return {
    offers,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StockItem)
