import React, { Component } from 'react'
import PropTypes from 'prop-types'
import BeneficiaryCell from './CellsFormatter/BeneficiaryCell'
import BookingDateCell from './CellsFormatter/BookingsDateCell'
import BookingStatusCell from './CellsFormatter/BookingsStatusCell'
import BookingTokenCell from './CellsFormatter/BookingsTokenCell'
import Table from './Table/Table'
import BookingOfferCell from './CellsFormatter/BookingOfferCell'
import IsDuoCell from './CellsFormatter/IsDuoCell'

class BookingsRecapTable extends Component {
  constructor(props) {
    super(props)
    this.state = {
      columns: [
        {
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          Cell: ({ value }) => <BookingOfferCell offer={value} />,
        },
        {
          headerTitle: '',
          accessor: 'booking_is_duo',
          Cell: ({ value }) => <IsDuoCell isDuo={value} />,
          className: 'td-bookings-duo',
        },
        {
          headerTitle: 'Bénéficiaire',
          accessor: 'beneficiary',
          Cell: ({ value }) => <BeneficiaryCell beneficiaryInfos={value} />,
        },
        {
          headerTitle: 'Réservation',
          accessor: 'booking_date',
          Cell: ({ value }) => <BookingDateCell bookingDate={value} />,
        },
        {
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
          Cell: ({ value }) => <BookingTokenCell bookingToken={value} />,
        },
        {
          headerTitle: 'Statut',
          accessor: 'booking_status',
          Cell: ({ value }) => <BookingStatusCell bookingStatus={value} />,
          className: 'bookings-status',
        },
      ],
    }
  }

  shouldComponentUpdate() {
    return true
  }

  render() {
    const { bookingsRecap } = this.props
    const { columns } = this.state

    return (
      <Table
        columns={columns}
        data={bookingsRecap}
      />
    )
  }
}

BookingsRecapTable.propTypes = {
  bookingsRecap: PropTypes.shape({}).isRequired,
}

export default BookingsRecapTable
