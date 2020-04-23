import React, {PureComponent} from 'react'
import {useTable} from 'react-table'
import BeneficiaryCell from "../CellsFormatter/BeneficiaryCell"
import BookingDateCell from "../CellsFormatter/BookingsDateCell"
import Table from "../Table/Table"


class BookingsTable extends PureComponent {
  constructor(props) {
    super(props)
  }

  render() {
    const columns = [
      {
        Header: 'Nom de l\'offre',
        accessor: 'stock',
        Cell: ({value}) => (
          <span className="offer-link">
          {value.offer_name}
        </span>),
      },
      {
        Header: 'Bénéficiaire',
        accessor: 'beneficiary',
        Cell: ({value}) => <BeneficiaryCell values={value}/>,
      },
      {
        Header: 'Réservation',
        accessor: 'booking_date',
        Cell: ({value}) => <BookingDateCell information={value}/>,
      },
      {
        Header: 'Contremarque',
        accessor: 'booking_token',
      },
    ]

    const { bookingsRecap } = this.props

    return (
      <Table columns={columns} data={bookingsRecap}/>
    )
  }
}


export default BookingsTable
