import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import { fetchBookingsRecapByPage } from '../../../services/bookingsRecapService'
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { bookingsRecap: [] }
  }

  componentDidMount() {
    fetchBookingsRecapByPage()
      .then(this.duplicateDuoBookings)
      .then(this.handleSuccess)
  }

  duplicateDuoBookings = paginatedBookingRecaps => {
    return paginatedBookingRecaps.bookings_recap
      .map(bookingRecap =>
        bookingRecap.booking_is_duo ? [bookingRecap, bookingRecap] : bookingRecap
      )
      .reduce((accumulator, currentValue) => accumulator.concat(currentValue), [])
  }

  handleSuccess = (bookingRecaps = {}) => {
    this.setState({ bookingsRecap: bookingRecaps })
  }

  render() {
    const { bookingsRecap } = this.state
    return (
      <Main name="bookings-v2">
        <Titles title="Réservations" />
        {bookingsRecap.length > 0 ? (
          <BookingsRecapTable bookingsRecap={bookingsRecap} />
        ) : (
          <NoBookingsMessage />
        )}
      </Main>
    )
  }
}

export default BookingsRecap
