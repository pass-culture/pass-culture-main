import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'

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
  const eventOrThingName = get(event, 'name') || get(thing, 'name')
  const type = get(offer, 'type')
  const offererName = get(offerer, 'name')
  const price = get(offer, 'price')
  const venueName = get(venue, 'name')

  return (
    <React.Fragment>
      <tr className="offer-item">
        <td colSpan="5" className="title">
          {eventOrThingName}
        </td>
        <td rowSpan="2">27/04/2018</td>
        <td rowSpan="2">5/10</td>
        <td rowSpan="2">{price}</td>
        <td rowSpan="2">4&euro;</td>
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
        <td>24/04/2018</td>
        <td>{type}</td>
        <td>{offererName}</td>
        <td>{venueName}</td>
        <td>
          {/*<Icon svg="picto-user" />*/}
          <Icon svg="picto-group" /> 5
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
