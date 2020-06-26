import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import Header from './Header/Header'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import { NB_BOOKINGS_PER_PAGE } from './NB_BOOKINGS_PER_PAGE'
import TableFrame from './Table/TableFrame'
import Filters from './Filters/Filters'
import { ALL_BOOKING_STATUS, ALL_VENUES, EMPTY_FILTER_VALUE } from './Filters/_constants'
import NoFilteredBookings from './NoFilteredBookings/NoFilteredBookings'
import findOldestBookingDate from './utils/findOldestBookingDate'
import filterBookingsRecap from './utils/filterBookingsRecap'
import FilterByBookingStatus from './Filters/FilterByBookingStatus'
import { sortByBeneficiaryName, sortByBookingDate, sortByOfferName } from './utils/sortingFunctions'

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
          Cell: ({ value }) => <BookingOfferCell offer={value} />,
          className: 'column-offer-name',
          defaultCanSort: true,
          sortType: sortByOfferName,
        },
        {
          id: 2,
          headerTitle: '',
          accessor: 'booking_is_duo',
          Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
          className: 'column-booking-duo',
          disableSortBy: true,
        },
        {
          id: 3,
          headerTitle: 'Bénéficiaire',
          accessor: 'beneficiary',
          Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
          className: 'column-beneficiary',
          defaultCanSort: true,
          sortType: sortByBeneficiaryName,
        },
        {
          id: 4,
          headerTitle: 'Réservation',
          accessor: 'booking_date',
          Cell: ({ value }) => <BookingDateCell bookingDate={value} />,
          className: 'column-booking-date',
          defaultCanSort: true,
          sortType: sortByBookingDate,
        },
        {
          id: 5,
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
          className: 'column-booking-token',
          disableSortBy: true,
        },
        {
          id: 6,
          accessor: 'booking_status',
          headerTitle: 'Statut',
          Cell: ({ row }) => <BookingStatusCell bookingRecapInfo={row} />,
          className: 'column-booking-status',
          disableSortBy: true,
          Filter: () => (
            <FilterByBookingStatus
              bookingsRecap={props.bookingsRecap}
              updateGlobalFilters={this.updateGlobalFilters}
            />
          ),
        },
      ],
      currentPage: FIRST_PAGE_INDEX,
      filters: {
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingBeginningDate: EMPTY_FILTER_VALUE,
        bookingEndingDate: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerDate: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        offerVenue: ALL_VENUES,
        bookingStatus: ALL_BOOKING_STATUS,
      },
      oldestBookingDate: findOldestBookingDate(props.bookingsRecap),
    }
    this.filtersRef = React.createRef()
  }

  componentDidUpdate(prevProps) {
    const { bookingsRecap } = this.props
    if (prevProps.bookingsRecap.length !== bookingsRecap.length) {
      this.applyFilters()
      this.setOldestBookingDate(bookingsRecap)
    }
  }

  setOldestBookingDate = bookingsRecap => {
    this.setState({
      oldestBookingDate: findOldestBookingDate(bookingsRecap),
    })
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
    const { bookingsRecapFiltered, columns, currentPage, oldestBookingDate } = this.state
    const nbBookings = bookingsRecapFiltered.length

    return (
      <div>
        <Filters
          isLoading={isLoading}
          oldestBookingDate={oldestBookingDate}
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

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default BookingsRecapTable
