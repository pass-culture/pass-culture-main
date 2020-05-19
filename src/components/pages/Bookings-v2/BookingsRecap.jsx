import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import { fetchBookingsRecapByPage } from '../../../services/bookingsRecapService'
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecap: [],
      apiPage: 0,
      apiPages: 0,
      total: 0,
    }
  }

  componentDidMount() {
    fetchBookingsRecapByPage()
      .then(this.updatePages)
      .then(this.handleSuccess)
  }

  componentDidUpdate() {
    let { apiPage, apiPages } = this.state
    if (apiPage < apiPages) {
      apiPage++
      fetchBookingsRecapByPage(apiPage).then(this.handleSuccess)
    }
  }

  updatePages = paginatedBookingRecaps => {
    return paginatedBookingRecaps
  }

  handleSuccess = (paginatedBookingRecaps = {}) => {
    const { bookingsRecap } = this.state
    this.setState({
      apiPage: paginatedBookingRecaps.page,
      apiPages: paginatedBookingRecaps.pages,
      bookingsRecap: [...bookingsRecap].concat(paginatedBookingRecaps.bookings_recap),
      total: paginatedBookingRecaps.total,
    })
  }

  render() {
    const { bookingsRecap, total } = this.state
    return (
      <Main name="bookings-v2">
        <Titles title="Réservations" />
        {bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            nbBookings={total}
          />
        ) : (
          <NoBookingsMessage />
        )}
      </Main>
    )
  }
}

export default BookingsRecap
