import { shallow } from 'enzyme'
import React from 'react'
import Table from '../Table'

describe('components | pages | bookings-v2 | table', () => {
  it('should display the correct numbers of columns', () => {
    // Given
    const props = {
      columns: [
        {
          headerTitle: 'Stock',
          accessor: 'stock',
        },
        {
          headerTitle: 'Beneficiaire',
          accessor: 'beneficiary',
        },
      ],
      data: [{}],
    }

    // When
    const table = shallow(<Table {...props} />)

    // Then
    const tableColumns = table.find('th')
    expect(tableColumns).toHaveLength(2)
  })

  it('should display the correct numbers of rows', () => {
    // Given
    const props = {
      columns: [
        {
          headerTitle: 'Stock',
          accessor: 'stock',
        },
        {
          headerTitle: 'Beneficiaire',
          accessor: 'beneficiary',
        },
      ],
      data: [
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
        },
        {
          stock: {
            offer_name: 'Avez-vous déjà vu',
          },
          beneficiary: {
            lastname: 'Klepi',
            firstname: 'Sonia',
            email: 'sonia.klepi@example.com',
          },
          booking_date: '2020-04-03T12:00:00Z',
          booking_token: 'ZEHBGD',
        },
      ],
    }

    // When
    const table = shallow(<Table {...props} />)

    // Then
    const tableRows = table.find('tbody > tr')
    expect(tableRows).toHaveLength(2)
  })
})
