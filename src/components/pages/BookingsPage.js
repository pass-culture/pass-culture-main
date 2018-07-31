import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import Main from '../layout/Main'
import selectBookingsByTime from '../../selectors/bookingsByTime'

class BookingsPage extends Component {
  handleDataRequest = () => {
    this.props.requestData('GET', 'bookings')
  }

  render() {
    const { soonBookings, otherBookings } = this.props.bookingsByTime
    return (
      <Main
        backButton
        handleDataRequest={this.handleDataRequest}
        name="bookings"
        menuButton={{ borderTop: true }}
        redBg>
        <header>
          <h1>Mes réservations</h1>
        </header>
        {soonBookings.length > 0 && (
          <div>
            <h4>C'est bientôt !</h4>
            <ul className="bookings">
              {soonBookings.map((b, index) => (
                <BookingItem key={index} {...b} />
              ))}
            </ul>
          </div>
        )}
        {otherBookings.length > 0 && (
          <div>
            <h4>Réservations</h4>
            <ul className="bookings">
              {otherBookings.map((b, index) => (
                <BookingItem key={index} {...b} />
              ))}
            </ul>
          </div>
        )}
        {soonBookings.length === 0 &&
          otherBookings.length === 0 && (
            <div>
              <p className="nothing">Pas encore de réservation.</p>
              <p className="nothing">
                <Link to="/decouverte" className="button is-primary">
                  Allez-y !
                </Link>
              </p>
            </div>
          )}
      </Main>
    )
  }
}

export default compose(
  connect(
    state => ({
      bookingsByTime: selectBookingsByTime(state),
    }),
    { requestData }
  )
)(BookingsPage)
