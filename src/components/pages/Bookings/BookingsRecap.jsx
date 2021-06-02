import * as PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { fetchBookingsRecapByPage } from 'repository/bookingsRecapService'

import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import BookingsRecapTableLegacy from './BookingsRecapTableLegacy/BookingsRecapTableLegacy' /* eslint-disable-line react/jsx-pascal-case */
import NoBookingsMessage from './NoBookingsMessage/NoBookingsMessage'
import { ALL_VENUES, EMPTY_FILTER_VALUE } from './PreFilters/_constants'
import PreFilters from './PreFilters/PreFilters'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecap: [],
      isLoading: true,
      page: 0,
      pages: 0,
      preFilters: {
        bookingBeginningDate: EMPTY_FILTER_VALUE,
        bookingEndingDate: EMPTY_FILTER_VALUE,
        offerDate: EMPTY_FILTER_VALUE,
        offerVenueId: ALL_VENUES,
      },
    }
  }

  componentDidMount() {
    this.fetchFirstBookingsRecapPage()
  }

  componentDidUpdate() {
    const { page, pages, preFilters } = this.state

    let currentPage = page
    if (currentPage < pages && currentPage < 5) {
      currentPage++
      fetchBookingsRecapByPage(currentPage, { venueId: preFilters.offerVenueId }).then(
        this.savePaginatedBookingsRecap
      )
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

  fetchFirstBookingsRecapPage() {
    const { preFilters } = this.state
    fetchBookingsRecapByPage(1, { venueId: preFilters.offerVenueId }).then(
      this.savePaginatedBookingsRecap
    )
  }

  applyPreFilters = selectedPreFilters => {
    this.setState(
      {
        isLoading: true,
        bookingsRecap: [],
        preFilters: { ...selectedPreFilters },
      },
      () => this.fetchFirstBookingsRecapPage()
    )
  }

  savePaginatedBookingsRecap = paginatedBookingsRecap => {
    const { bookingsRecap } = this.state

    if (paginatedBookingsRecap.page === 1) {
      this.setState({
        bookingsRecap: paginatedBookingsRecap.bookings_recap,
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
      <AppLayout layoutConfig={{ pageName: 'bookings' }}>
        <PageTitle title="Vos réservations" />
        <Titles title="Réservations" />
        {this.props.arePreFiltersEnabled ? (
          <>
            <PreFilters
              applyPreFilters={this.applyPreFilters}
              offerVenueId={locationState?.venueId}
            />
            {bookingsRecap.length > 0 && (
              <BookingsRecapTable
                bookingsRecap={bookingsRecap}
                isLoading={isLoading}
                locationState={locationState}
              />
            )}
          </>
        ) : bookingsRecap.length > 0 ? (
          <BookingsRecapTableLegacy
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

BookingsRecap.propTypes = {
  arePreFiltersEnabled: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape({
      venueId: PropTypes.string,
      statuses: PropTypes.arrayOf(PropTypes.string),
    }),
  }).isRequired,
  showWarningNotification: PropTypes.func.isRequired,
}

export default BookingsRecap
