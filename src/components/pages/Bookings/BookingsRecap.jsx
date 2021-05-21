import * as PropTypes from 'prop-types'
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
    if (currentPage < pages && currentPage < 5) {
      currentPage++
      fetchBookingsRecapByPage(currentPage).then(this.savePaginatedBookingsRecap)
    } else {
      this.loadData()
      if (currentPage === 5 && currentPage < pages) {
        this.props.showWarningNotification()
      }
    }
  }

  loadData = () => {
    this.setState({
      isLoading: false,
    })
  }

  savePaginatedBookingsRecap = paginatedBookingsRecap => {
    const { bookingsRecap } = this.state

    if (paginatedBookingsRecap.page === 1) {
      this.setState({
        bookingsRecap: [...bookingsRecap].concat(paginatedBookingsRecap.bookings_recap),
        page: paginatedBookingsRecap.page,
        pages: paginatedBookingsRecap.pages,
      })
    } else {
      this.setState({
        bookingsRecap: [...bookingsRecap].concat(paginatedBookingsRecap.bookings_recap),
        page: paginatedBookingsRecap.page,
      })
    }
  }

  render() {
    const { bookingsRecap, isLoading } = this.state
    const { state: locationState } = this.props.location

    return (
      <AppLayout layoutConfig={{ pageName: 'bookings-v2' }}>
        <PageTitle title="Vos réservations" />
        <Titles title="Réservations" />
        {bookingsRecap.length > 0 ? (
          <BookingsRecapTable
            bookingsRecap={bookingsRecap}
            isLoading={isLoading}
            locationState={locationState}
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

BookingsRecap.propTypes = {
  location: PropTypes.shape({
    state: PropTypes.shape({
      venueId: PropTypes.string,
      statuses: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
  showWarningNotification: PropTypes.func.isRequired,
}
