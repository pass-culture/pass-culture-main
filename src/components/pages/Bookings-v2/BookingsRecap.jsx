import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import { API_URL } from '../../../utils/config'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { bookingsRecap: [] }
  }

  componentDidMount() {
    fetch(`${API_URL}/bookings/pro`, { credentials: 'include' })
      .then(response => response.json())
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
      <Main name="bookings-v2">
        <Titles title="Réservations V2" />
        <BookingsRecapTable bookingsRecap={bookingsRecap} />
      </Main>
    )
  }
}

export default BookingsRecap
