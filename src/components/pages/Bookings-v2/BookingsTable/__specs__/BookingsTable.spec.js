import BookingsTable from "../BookingsTable"
import React from "react"
import { shallow } from 'enzyme'

describe('components | pages | Bookings-v2 | BookingsTable', function () {
  it('should render a Table component with columns and data', function () {
    // Given
    const expectedColumns = [
      {
        Header: 'Nom de l\'offre',
        accessor: 'stock',
        Cell: ({value}) => <span className={"offer-link"}>{value.offer_name}</span>,
      },
      {
        Header: 'Bénéficiaire',
        accessor: 'beneficiary',
        Cell: ({value}) => <BeneficiaryCell values={value}/>,
      },
      {
        Header: 'Réservation',
        accessor: 'booking_date',
        Cell: ({value}) => <BookingDateCell values={value}/>,
      },
      {
        Header: 'Contremarque',
        accessor: 'booking_token',
      },
    ]

    const data = [
      {
        'stock': {
          'offer_name': 'Avez-vous déjà vu',
        },
        'beneficiary': {
          'lastname': 'Klepi',
          'firstname': 'Sonia',
          'email': 'sonia.klepi@example.com',
        },
        'booking_date': '2020-04-03T12:00:00Z',
        'booking_token': 'ZEHBGD',
      },
      {
        'stock': {
          'offer_name': 'Avez-vous déjà vu',
        },
        'beneficiary': {
          'lastname': 'Klepi',
          'firstname': 'Sonia',
          'email': 'sonia.klepi@example.com',
        },
        'booking_date': '2020-04-03T12:00:00Z',
        'booking_token': 'ZEHBGD',
      },
    ]

    const props = {
      'bookingsRecap': data,
    }

    // When
    const wrapper = shallow(<BookingsTable {...props}/>)
    const table = wrapper.find('Table')

    // Then
    console.log(table)
    expect()
  })
})
