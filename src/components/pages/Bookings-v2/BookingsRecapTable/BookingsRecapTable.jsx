import React, { Component } from 'react'
import PropTypes from 'prop-types'
import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingDateCell'
import BookingStatusCell from './CellsFormatter/BookingStatusCell'
import BookingTokenCell from './CellsFormatter/BookingTokenCell'
import Table from './Table/Table'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import Header from './Header/Header'
import BookingIsDuoCell from './CellsFormatter/BookingIsDuoCell'
import { NB_BOOKINGS_PER_PAGE } from './NB_BOOKINGS_PER_PAGE'

class BookingsRecapTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      columns: [
        {
          id: 1,
          headerTitle: "Nom de l'offre",
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
    }
  }

  shouldComponentUpdate() {
    return true
  }

  updateCurrentPage = currentPage => {
    this.setState({
      currentPage: currentPage,
    })
  }

  render() {
    const { bookingsRecap, nbBookings } = this.props
    const { columns, currentPage } = this.state

    return (
      <div>
        <Header nbBookings={nbBookings} />
        <Table
          columns={columns}
          currentPage={currentPage}
          data={bookingsRecap}
          nbBookings={nbBookings}
          nbBookingsPerPage={NB_BOOKINGS_PER_PAGE}
          updateCurrentPage={this.updateCurrentPage}
        />
      </div>
    )
  }
}

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  nbBookings: PropTypes.number.isRequired,
}

export default BookingsRecapTable
