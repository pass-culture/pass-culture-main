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
      isLoading: true,
      page: 0,
      pages: 0,
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
      this.loadData()
    }
  }

  loadData = () => {
    this.setState({
      isLoading:false
    })
  }

  savePaginatedBookingsRecap = paginatedBookingsRecap => {
    const { bookingsRecap } = this.state

    this.setState({
      bookingsRecap: [...bookingsRecap].concat(paginatedBookingsRecap.bookings_recap),
      page: paginatedBookingsRecap.page,
      pages: paginatedBookingsRecap.pages,
    })
  }

  render() {
    const { bookingsRecap, isLoading } = this.state

    return (
      <Main name="bookings-v2">
        <Titles title="Réservations" />
        {bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isLoading={isLoading}
          />
        ) : (
          isLoading ? <Spinner /> : <NoBookingsMessage />
        )}
      </Main>
    )
  }
}

export default BookingsRecap
