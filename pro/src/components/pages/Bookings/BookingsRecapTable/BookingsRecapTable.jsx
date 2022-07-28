import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'

import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import {
  ALL_BOOKING_STATUS,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './Filters/_constants'
import FilterByBookingStatus from './Filters/FilterByBookingStatus'
import FilterByOmniSearch from './Filters/FilterByOmniSearch'
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
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
          className: 'column-booking-token',
          disableSortBy: true,
        },
        {
          id: 6,
          accessor: 'booking_status',
          Cell: ({ row }) => <BookingStatusCell bookingRecapInfo={row} />,
          className: 'column-booking-status',
          disableSortBy: true,
          HeaderTitleFilter: () => (
            <FilterByBookingStatus
              bookingStatuses={this.state.bookingStatus}
              bookingsRecap={props.bookingsRecap}
              updateGlobalFilters={this.updateGlobalFilters}
            />
          ),
        },
      ],
      currentPage: FIRST_PAGE_INDEX,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingStatus: props.locationState?.statuses.length
        ? props.locationState.statuses
        : [...ALL_BOOKING_STATUS],
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      keywords: '',
    }
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
    const { filters } = {
      currentPage: this.state.currentPage,
      bookingBeneficiary: this.state.bookingBeneficiary,
      bookingToken: this.state.bookingToken,
      offerISBN: this.state.offerISBN,
      offerName: this.state.offerName,
      bookingStatus: this.state.bookingStatus,
    }

    this.setState(
      {
        ...filters,
        ...updatedFilters,
      },
      () => this.applyFilters()
    )
  }

  applyFilters = filtersBookingResults => {
    const { bookingsRecap } = this.props
    const filters = filtersBookingResults || {
      currentPage: this.state.currentPage,
      bookingBeneficiary: this.state.bookingBeneficiary,
      bookingToken: this.state.bookingToken,
      offerISBN: this.state.offerISBN,
      offerName: this.state.offerName,
      bookingStatus: this.state.bookingStatus,
    }
    const bookingsRecapFiltered = filterBookingsRecap(bookingsRecap, filters)

    this.setState({
      bookingsRecapFiltered: bookingsRecapFiltered,
      currentPage: FIRST_PAGE_INDEX,
    })
  }

  resetAllFilters = () => {
    const filtersBookingResults = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingStatus: [...ALL_BOOKING_STATUS],
      keywords: EMPTY_FILTER_VALUE,
    }
    this.setState(filtersBookingResults)
    this.applyFilters(filtersBookingResults)
  }

  updateFilters = (updatedFilter, updatedSelectedContent) => {
    const { keywords, selectedOmniSearchCriteria } = updatedSelectedContent
    this.setState({ ...updatedFilter, keywords, selectedOmniSearchCriteria })
    this.applyFilters({
      bookingBeneficiary: this.state.bookingBeneficiary,
      bookingToken: this.state.bookingToken,
      offerISBN: this.state.offerISBN,
      offerName: this.state.offerName,
      bookingStatus: this.state.bookingStatus,
      keywords: this.state.keywords,
      ...updatedFilter,
    })
  }

  render() {
    const { isLoading } = this.props
    const { bookingsRecapFiltered, columns, currentPage } = this.state
    const nbBookings = bookingsRecapFiltered.length

    return (
      <div>
        <div className="filters-wrapper">
          <FilterByOmniSearch
            isDisabled={isLoading}
            keywords={this.state.keywords}
            selectedOmniSearchCriteria={this.state.selectedOmniSearchCriteria}
            updateFilters={this.updateFilters}
          />
        </div>
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
          <NoFilteredBookings resetFilters={this.resetAllFilters} />
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
