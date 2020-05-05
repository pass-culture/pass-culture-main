import React, { PureComponent } from 'react'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingsDateCell'
import BookingStatusCell from '../CellsFormatter/BookingsStatusCell'
import Table from '../Table/Table'

class BookingsRecapTable extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      columns: [
        {
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          Cell: ({ value }) => (<span className="cell-offer-link">
            {value.offer_name}
          </span>),
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
        },
        {
          headerTitle: 'Statut',
          accessor: 'booking_status',
          Cell: ({ value }) => <BookingStatusCell bookingStatus={value} />,
          className: 'td-bookings-status',
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
