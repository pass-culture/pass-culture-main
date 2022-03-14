import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'

import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import { ALL_BOOKING_STATUS, EMPTY_FILTER_VALUE } from './Filters/_constants'
import FilterByBookingStatus from './Filters/FilterByBookingStatus'
import Filters from './Filters/Filters'
import Header from './Header/Header'
import { NB_BOOKINGS_PER_PAGE } from './NB_BOOKINGS_PER_PAGE'
import NoFilteredBookings from './NoFilteredBookings/NoFilteredBookings'
import TableFrame from './Table/TableFrame'
import filterBookingsRecap from './utils/filterBookingsRecap'
import {
  sortByBeneficiaryName,
  sortByBookingDate,
  sortByOfferName,
} from './utils/sortingFunctions'

const FIRST_PAGE_INDEX = 0

class BookingsRecapTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecapFiltered: props.bookingsRecap,
      columns: [
        {
          id: 1,
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ value }) => <BookingOfferCell offer={value} />,
          className: 'column-offer-name',
          defaultCanSort: true,
          sortType: sortByOfferName,
        },
        {
          id: 2,
          headerTitle: '',
          accessor: 'booking_is_duo',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
          className: 'column-booking-duo',
          disableSortBy: true,
        },
        {
          id: 3,
          headerTitle: 'Bénéficiaire',
          accessor: 'beneficiary',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
          className: 'column-beneficiary',
          defaultCanSort: true,
          sortType: sortByBeneficiaryName,
        },
        {
          id: 4,
          headerTitle: 'Réservation',
          accessor: 'booking_date',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ value }) => (
            <BookingDateCell bookingDateTimeIsoString={value} />
          ),
          className: 'column-booking-date',
          defaultCanSort: true,
          sortType: sortByBookingDate,
        },
        {
          id: 5,
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
          className: 'column-booking-token',
          disableSortBy: true,
        },
        {
          id: 6,
          accessor: 'booking_status',
          /* eslint-disable react/no-unstable-nested-components */
          Cell: ({ row }) => <BookingStatusCell bookingRecapInfo={row} />,
          className: 'column-booking-status',
          disableSortBy: true,
          HeaderTitleFilter: () => (
            <FilterByBookingStatus
              bookingStatuses={this.state.filters.bookingStatus}
              bookingsRecap={props.bookingsRecap}
              updateGlobalFilters={this.updateGlobalFilters}
            />
          ),
        },
      ],
      currentPage: FIRST_PAGE_INDEX,
      filters: {
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        bookingStatus: props.locationState?.statuses.length
          ? props.locationState.statuses
          : [...ALL_BOOKING_STATUS],
      },
    }
    this.filtersRef = React.createRef()
  }

  componentDidMount() {
    this.applyFilters()
  }

  componentDidUpdate(prevProps) {
    const { bookingsRecap } = this.props
    if (prevProps.bookingsRecap.length !== bookingsRecap.length) {
      this.applyFilters()
    }
  }

  updateCurrentPage = currentPage => {
    this.setState({
      currentPage: currentPage,
    })
  }

  updateGlobalFilters = updatedFilters => {
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          ...updatedFilters,
        },
      },
      () => this.applyFilters()
    )
  }

  applyFilters = () => {
    const { bookingsRecap } = this.props
    const { filters } = this.state
    const bookingsRecapFiltered = filterBookingsRecap(bookingsRecap, filters)

    this.setState({
      bookingsRecapFiltered: bookingsRecapFiltered,
      currentPage: FIRST_PAGE_INDEX,
    })
  }

  resetFilters = () => {
    this.filtersRef.current.resetAllFilters()
  }

  render() {
    const { isLoading } = this.props
    const { bookingsRecapFiltered, columns, currentPage } = this.state
    const nbBookings = bookingsRecapFiltered.length

    return (
      <div>
        <Filters
          isLoading={isLoading}
          ref={this.filtersRef}
          updateGlobalFilters={this.updateGlobalFilters}
        />
        {nbBookings > 0 ? (
          <Fragment>
            <Header
              bookingsRecapFiltered={bookingsRecapFiltered}
              isLoading={isLoading}
            />
            <TableFrame
              columns={columns}
              currentPage={currentPage}
              data={bookingsRecapFiltered}
              nbBookings={nbBookings}
              nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
              updateCurrentPage={this.updateCurrentPage}
            />
          </Fragment>
        ) : (
          <NoFilteredBookings resetFilters={this.resetFilters} />
        )}
      </div>
    )
  }
}

BookingsRecapTable.defaultProps = {
  locationState: null,
}

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  isLoading: PropTypes.bool.isRequired,
  locationState: PropTypes.shape({
    venueId: PropTypes.string,
    statuses: PropTypes.arrayOf(PropTypes.string),
  }),
}

export default BookingsRecapTable
