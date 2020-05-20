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
      apiPage: 0,
      apiPages: 0,
      bookingsRecap: [],
      nbBookings: 0,
    }
  }

  componentDidMount() {
    fetchBookingsRecapByPage().then(this.handleSuccess)
  }

  componentDidUpdate() {
    const { apiPage, apiPages } = this.state

    let currentApiPage = apiPage
    if (currentApiPage < apiPages) {
      currentApiPage++
      fetchBookingsRecapByPage(currentApiPage).then(this.handleSuccess)
    }
  }

  handleSuccess = (paginatedBookingRecaps = {}) => {
    const { bookingsRecap } = this.state

    this.setState({
      apiPage: paginatedBookingRecaps.page,
      apiPages: paginatedBookingRecaps.pages,
      bookingsRecap: [...bookingsRecap].concat(paginatedBookingRecaps.bookings_recap),
      nbBookings: paginatedBookingRecaps.total,
    })
  }

  render() {
    const { bookingsRecap, nbBookings } = this.state

    return (
      <Main name="bookings-v2">
        <Titles title="Réservations" />
        {nbBookings > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            nbBookings={nbBookings}
          />
        ) : (
          <NoBookingsMessage />
        )}
      </Main>
    )
  }
}

export default BookingsRecap
