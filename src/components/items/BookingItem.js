import get from 'lodash.get'
import { Icon, requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import moment from 'moment'

import eventSelector from '../../selectors/event'
import thingSelector from '../../selectors/thing'
import offerSelector from '../../selectors/offer'
import offererSelector from '../../selectors/offerer'
import selectEventOccurrenceById from '../../selectors/selectEventOccurenceById'
import selectStockById from '../../selectors/selectStockById'
import venueSelector from '../../selectors/venue'

const getBookingState = booking => {
  const map = {
    payement: 'picto-validation',
    validation: 'picto-encours-S',
    pending: 'picto-temps-S',
    error: 'picto-warning',
    cancel: 'picto-warning',
  }

  console.log(booking)
  if (booking.isCancelled === true) {
    return {
      picto: map.cancel,
      message: 'Annulé',
    }
  }

  return {
    picto: map.pending,
    message: 'En attente',
  }

}

const BookingItem = ({
  booking,
  event,
  eventOccurrence,
  offer,
  offerer,
  stock,
  thing,
  venue,
  cancelAction,
}) => {
  // TODO: we need to continue to extract the
  // view attributes from the data
  const eventOrThing = event || thing
  const eventOrThingName = get(event, 'name') || get(thing, 'name')
  const type = get(offer, 'type')
  const offererName = get(offerer, 'name')
  const venueName = get(venue, 'name')
  const bookingState = getBookingState(booking)

  return (
    <React.Fragment>
      <tr className="offer-item">
        <td colSpan="5" className="title">
          {eventOrThingName}
        </td>
        <td colspan="5" className="title userName">
          UserId: {booking.userId} - BookingId: {booking.id} - Token:{' '}
          {booking.token}
        </td>
        <td rowSpan="2">
          <div className="navbar-item has-dropdown is-hoverable AccountingPage-actions">
            <div className="actionButton" />

            <div className="navbar-dropdown is-right">
              <a
                className="navbar-item cancel"
                onClick={() => {
                  if (window.confirm('Annuler cette réservation ?')) {
                    cancelAction(booking.id)
                  }
                }}>
                <Icon svg="ico-close-r" /> Annuler la réservation
              </a>
            </div>
          </div>
        </td>
      </tr>
      <tr className="offer-item first-col">
        <td>{moment(booking.dateModified).format('D/MM/YY')}</td>
        <td>{eventOrThing.type}</td>
        <td>{offererName}</td>
        <td>{venueName}</td>
        <td>
          {stock.groupSize === 1 && <Icon svg="picto-user" />}
          {stock.groupSize > 1 && (
            <React.Fragment>
              <Icon svg="picto-group" /> {stock.groupSize}
            </React.Fragment>
          )}
        </td>
        <td>{moment(stock.bookingLimitDatetime).format('D/MM/YY')}</td>
        <td>5/10</td>
        <td>{booking.amount}</td>
        <td>{booking.reimbursed_amount}</td>
        <td>
          <Icon svg={bookingState.picto} className="picto tiny" />{' '}
          {bookingState.message}
        </td>
      </tr>
    </React.Fragment>
  )
}

BookingItem.propTypes = {
  booking: PropTypes.object.isRequired,
}

export default connect((state, ownProps) => {
  const stock = selectStockById(state, ownProps.booking.stockId)
  const eventOccurrence = selectEventOccurrenceById(
    state,
    get(stock, 'eventOccurrenceId')
  )
  const offer = offerSelector(
    state,
    get(stock, 'offerId') || get(eventOccurrence, 'offerId')
  )
  const event = eventSelector(state, get(offer, 'eventId'))
  const thing = thingSelector(state, get(offer, 'thingId'))
  const venue = venueSelector(state, get(offer, 'venueId'))
  const offerer = offererSelector(state, get(venue, 'managingOffererId'))
  return {
    event,
    eventOccurrence,
    offer,
    offerer,
    stock,
    thing,
    venue,
  }
})(BookingItem)
