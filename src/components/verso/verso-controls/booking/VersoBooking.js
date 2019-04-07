/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectBookings } from '../../../../selectors/selectBookings'
import currentRecommendation from '../../../../selectors/currentRecommendation'
import CancelButton from './CancelButton'
import BookThisButton from './BookThisButtonContainer'

export const RawVersoBookingButton = ({ booking }) => (
  <React.Fragment>
    {booking && <CancelButton booking={booking} />}
    {!booking && <BookThisButton />}
  </React.Fragment>
)

RawVersoBookingButton.defaultProps = {
  booking: null,
}

RawVersoBookingButton.propTypes = {
  booking: PropTypes.object,
}

const mapStateToProps = (state, { match }) => {
  const { mediationId, offerId } = match.params
  const recommendation = currentRecommendation(state, offerId, mediationId)
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  return {
    booking,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawVersoBookingButton)
