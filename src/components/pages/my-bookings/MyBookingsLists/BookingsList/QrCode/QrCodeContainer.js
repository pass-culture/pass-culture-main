import { compose } from 'redux'
import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'

import QrCode from './QrCode'
import { selectBookingByRouterMatch } from '../../../../../../selectors/data/bookingsSelectors'
import { getTimezone } from '../../../../../../utils/timezone'
import { humanizeDate } from '../../../../../../utils/date/date'
import { selectOfferById } from '../../../../../../selectors/data/offersSelectors'
import { selectStockById } from '../../../../../../selectors/data/stocksSelectors'

export const mapStateToProps = (state, props) => {
  const { match } = props
  const booking = selectBookingByRouterMatch(state, match)
  const { stockId } = booking || {}
  const stock = selectStockById(state, stockId)
  const { beginningDatetime, offerId } = stock
  const offer = selectOfferById(state, offerId)
  const { name: offerName, venue } = offer
  const { departementCode, name: venueName } = venue
  const { qrCode, token } = booking
  const timezone = getTimezone(departementCode)
  const humanizedBeginningDatetime = beginningDatetime
    ? humanizeDate(beginningDatetime, timezone)
    : ''

  return {
    humanizedBeginningDatetime,
    offerName,
    qrCode,
    token,
    venueName,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(QrCode)
