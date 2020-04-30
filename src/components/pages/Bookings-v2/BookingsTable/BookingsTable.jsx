import React, { PureComponent } from 'react'
import BeneficiaryCell from '../CellsFormatter/BeneficiaryCell'
import BookingDateCell from '../CellsFormatter/BookingsDateCell'
import Table from '../Table/Table'
import BookingStatusCell from '../CellsFormatter/BookingsStatusCell'

class BookingsTable extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      columns: [
        {
          headerTitle: "Nom de l'offre",
          accessor: 'stock',
          Cell: ({ value }) => (<span className="offer-link">
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
          Cell: ({ value }) => <BookingDateCell bookingDateInfos={value} />,
        },
        {
          headerTitle: 'Contremarque',
          accessor: 'booking_token',
        },
        {
          headerTitle: 'Status',
          accessor: 'booking_status',
          Cell: ({ value }) => <BookingStatusCell bookingStatusInfos={value} />,
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

export default BookingsTable
