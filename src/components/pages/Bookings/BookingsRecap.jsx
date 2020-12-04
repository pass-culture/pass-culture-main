import React, { PureComponent } from 'react'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { fetchBookingsRecapByPage } from 'repository/bookingsRecapService'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'

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
      isLoading: false,
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
      <AppLayout layoutConfig={{ pageName: 'bookings-v2' }}>
        <PageTitle title="Vos réservations" />
        <Titles title="Réservations" />
        {bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isLoading={isLoading}
          />
        ) : isLoading ? (
          <Spinner />
        ) : (
          <NoBookingsMessage />
        )}
      </AppLayout>
    )
  }
}

export default BookingsRecap
