import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'
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

const statePictoMap = {
  payement: 'picto-validation',
  validation: 'picto-encours-S',
  pending: 'picto-temps-S',
  error: 'picto-echec',
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
}) => {
  // TODO: we need to continue to extract the
  // view attributes from the data
  const eventOrThing = event || thing
  const eventOrThingName = get(event, 'name') || get(thing, 'name')
  const type = get(offer, 'type')
  const offererName = get(offerer, 'name')
  const venueName = get(venue, 'name')

  return (
    <React.Fragment>
      <tr className="offer-item">
        <td colSpan="5" className="title">
          {eventOrThingName}
        </td>
        <td rowSpan="2">
          {moment(stock.bookingLimitDatetime).format('D/MM/YYYY')}
        </td>
        <td rowSpan="2">5/10</td>
        <td rowSpan="2">{booking.amount}</td>
        <td rowSpan="2">{booking.reimbursed_amount}</td>
        <td rowSpan="2">
          <Icon svg={statePictoMap['payement']} className="picto tiny" /> Réglé
        </td>
        <td rowSpan="2">
          <button
            className="actionButton"
            type="button"
            onClick={() => {
              if (window.confirm('Annuler cette réservation ?')) {
                console.log('ok')
              } else {
                console.log('ko')
              }
            }}
          />
        </td>
      </tr>
      <tr className="offer-item first-col">
        <td>{moment(booking.dateModified).format('D/MM/YYYY')}</td>
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
