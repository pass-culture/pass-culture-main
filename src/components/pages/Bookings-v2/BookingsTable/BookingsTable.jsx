import React from 'react'
import BeneficiaryCell from "../CellsFormatter/BeneficiaryCell"
import BookingDateCell from "../CellsFormatter/BookingsDateCell"
import Table from "../Table/Table"

function BookingsTable(props) {
  const {bookingsRecap} = props
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
      Cell: ({value}) => <BeneficiaryCell values={value} />,
    },
    {
      Header: 'Réservation',
      accessor: 'booking_date',
      Cell: ({value}) => <BookingDateCell values={value} />,
    },
    {
      Header: 'Contremarque',
      accessor: 'booking_token',
    },
  ]

  return (
    <Table
      columns={columns}
      data={bookingsRecap}
    />
    )
}


export default BookingsTable
