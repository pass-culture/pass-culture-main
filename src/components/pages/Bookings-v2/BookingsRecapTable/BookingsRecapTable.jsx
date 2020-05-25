import React, { Component } from 'react'
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
import NoFilteredBookings from './NoFilteredBookings/NoFilteredBookings'

class BookingsRecapTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingsRecapFiltered: props.bookingsRecap,
      columns: [
        {
          id: 1,
          headerTitle: 'Nom de l\'offre',
          accessor: 'stock',
          Cell: ({ value }) => <BookingOfferCell offer={value} />,
          className: 'td-offer-name',
        },
        {
          id: 2,
          headerTitle: '',
          accessor: 'booking_is_duo',
          Cell: ({ value }) => <BookingIsDuoCell isDuo={value} />,
          className: 'td-booking-duo',
        },
        {
          id: 3,
          headerTitle: 'Bénéficiaire',
          accessor: 'beneficiary',
          Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
          className: 'td-beneficiary',
        },
        {
          id: 4,
          headerTitle: 'Réservation',
          accessor: 'booking_date',
          Cell: ({ value }) => <BookingDateCell bookingDate={value} />,
          className: 'td-booking-date',
        },
        {
          id: 5,
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
          className: 'td-booking-token',
        },
        {
          id: 6,
          headerTitle: 'Statut',
          accessor: 'booking_status',
          Cell: ({ value }) => <BookingStatusCell bookingStatus={value} />,
          className: 'td-booking-status',
        },
      ],
      currentPage: 0,
      filters: {
        offerName: '',
      },
    }
  }

  shouldComponentUpdate() {
    return true
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

  setFilters = filters => {
    this.setState({ filters: filters }, () => this.applyFilters())
  }

  applyFilters = () => {
    const { bookingsRecap } = this.props
    const {
      filters: { offerName },
    } = this.state

    const bookingsRecapFiltered = bookingsRecap.filter(booking => {
      const offerNameFromBooking = booking.stock.offer_name.toLowerCase()
      return offerNameFromBooking.includes(offerName.toLowerCase())
    })

    this.setState({
      bookingsRecapFiltered: bookingsRecapFiltered,
    })
  }

  render() {
    const { isLoading } = this.props
    const { bookingsRecapFiltered, columns, currentPage } = this.state
    const nbBookings = bookingsRecapFiltered.length

    return (
      <div>
        <Filters setFilters={this.setFilters} />
        <Header
          isLoading={isLoading}
          nbBookings={nbBookings}
        />
        {nbBookings > 0 ?
          <TableFrame
            columns={columns}
            currentPage={currentPage}
            data={bookingsRecapFiltered}
            nbBookings={nbBookings}
            nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
            updateCurrentPage={this.updateCurrentPage}
          />
          :
          <NoFilteredBookings setFilters={this.setFilters} />}
      </div>
    )
  }
}

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default BookingsRecapTable
