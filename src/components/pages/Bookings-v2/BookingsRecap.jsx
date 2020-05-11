import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import { fetchBookingRecaps } from '../../../services/bookingRecapsService'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { bookingsRecap: [] }
  }

  componentDidMount() {
    fetchBookingRecaps()
      .then(this.duplicateDuoBookings)
      .then(this.handleSuccess)
  }

  duplicateDuoBookings = bookingRecaps => {
    return bookingRecaps
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
      <Main
        fullwidthContent
        name="bookings-v2"
      >
        <Titles
          title="Réservations V2"
          withSectionIcon={false}
        />
        <BookingsRecapTable bookingsRecap={bookingsRecap} />
      </Main>
    )
  }
}

export default BookingsRecap
