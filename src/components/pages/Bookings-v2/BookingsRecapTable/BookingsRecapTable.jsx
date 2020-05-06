import React, { PureComponent } from 'react'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingsDateCell'
import BookingStatusCell from '../CellsFormatter/BookingsStatusCell'
import BookingTokenCell from '../CellsFormatter/BookingsTokenCell'
import Table from '../Table/Table'
import BookingOfferCell from '../CellsFormatter/BookingOfferCell'

class BookingsRecapTable extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      columns: [
        {
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          Cell: ({ value }) => <BookingOfferCell stock={value} />,
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

  render() {
    const { bookingsRecap } = this.props
    const { columns } = this.state
    return (<Table
      columns={columns}
      data={bookingsRecap}
            />)
  }
}

export default BookingsRecapTable
