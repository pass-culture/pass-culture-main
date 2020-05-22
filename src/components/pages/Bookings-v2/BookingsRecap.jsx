import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import { fetchBookingsRecapByPage } from '../../../services/bookingsRecapService'
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'
import Spinner from '../../layout/Spinner'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecap: [],
      nbBookings: 0,
      page: 0,
      pages: 0,
      isLoading: true,
    }
  }

  componentDidMount() {
    fetchBookingsRecapByPage().then(this.savePaginatedBookingsRecap)
  }

  componentDidUpdate() {
    const { page, pages } = this.state

    let currentPage = page
    if (currentPage < pages) {
      currentPage++
      fetchBookingsRecapByPage(currentPage).then(this.savePaginatedBookingsRecap)
    } else {
      this.setState({
        isLoading:false
      })
    }
  }

  savePaginatedBookingsRecap = paginatedBookingsRecap => {
    const { bookingsRecap } = this.state

    this.setState({
      bookingsRecap: [...bookingsRecap].concat(paginatedBookingsRecap.bookings_recap),
      nbBookings: paginatedBookingsRecap.total,
      page: paginatedBookingsRecap.page,
      pages: paginatedBookingsRecap.pages,
    })
  }

  render() {
    const { bookingsRecap, isLoading, nbBookings } = this.state

    return (
      <Main name="bookings-v2">
        <Titles title="Réservations" />
        {nbBookings > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isLoading={isLoading}
            nbBookings={nbBookings}
          />
        ) : (
          isLoading ? <Spinner/> : <NoBookingsMessage/>
        )}
      </Main>
    )
  }
}

export default BookingsRecap
