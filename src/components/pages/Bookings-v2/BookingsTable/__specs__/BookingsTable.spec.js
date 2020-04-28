import BookingsTable from "../BookingsTable"
import React from "react"
import {shallow} from 'enzyme'

describe('components | pages | Bookings-v2 | BookingsTable', function () {
  it('should call the Table component with columns and data props', function () {
    // Given
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
    const wrapper = shallow(<BookingsTable {...props} />)
    const table = wrapper.find('Table')

    // Then
    expect(table).toHaveLength(1)
    const tableProps = table.props()
    expect(tableProps['columns'].length).toBe(4)
    expect(tableProps['data'].length).toBe(2)
  })
})
