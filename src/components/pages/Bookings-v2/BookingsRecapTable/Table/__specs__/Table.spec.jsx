import { mount, shallow } from 'enzyme'
import { useTable } from 'react-table'
import React from 'react'
import Table from '../Table'
import Paginate from '../Paginate/Paginate'
import Head from '../Head/Head'

const CellMock = ({ offer: { offer_name: offerName } }) => (<span>
  {offerName}
</span>)

jest.mock('react-table', () => ({
  usePagination: jest.fn(),
  useTable: jest.fn(),
}))

describe('components | Table', () => {
  it('should display the correct given numbers of columns', () => {
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
      nbHitsPerPage: 1,
    }

    // When
    const table = shallow(<Table {...props} />)

    // Then
    const tableColumns = table.find('th')
    expect(tableColumns).toHaveLength(2)
  })

  it('should render a Head component with the right props', function() {
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
      nbHitsPerPage: 1,
    }
    const mockedValues = {
      canPreviousPage: true,
      canNextPage: true,
      getTableProps: jest.fn(),
      getTableBodyProps: jest.fn(),
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => (<span>
                {'Offres'}
              </span>)),
            },
            {
              id: 2,
              headerTitle: 'Beneficiaires',
              render: jest.fn(() => (<span>
                {'Beneficiaires'}
              </span>)),
            },
          ],
        },
      ],
      nextPage: jest.fn(),
      previousPage: jest.fn(),
      prepareRow: jest.fn(),
      page: [],
      pageCount: 1,
      state: {
        pageIndex: 0,
      },
    }
    useTable.mockReturnValue(mockedValues)

    // When
    const table = shallow(<Table {...props} />)

    // Then
    const tableHead = table.find(Head)
    expect(tableHead).toHaveLength(1)
    expect(tableHead.props()).toStrictEqual({
      headerGroups: mockedValues.headerGroups,
    })
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
      nbHitsPerPage: 2,
    }

    // When
    const table = shallow(<Table {...props} />)

    // Then
    const tableRows = table.find('tbody > tr')
    expect(tableRows).toHaveLength(2)
  })

  describe('pagination', () => {
    it('should render a Paginate component with the right props', () => {
      // Given
      const props = {
        columns: [
          {
            headerTitle: 'Stock',
            accessor: 'stock',
            // eslint-disable-next-line react/display-name, react/no-multi-comp
            Cell: ({ value }) => <CellMock offer={value} />,
          },
        ],
        data: [
          { stock: { offer_name: 'Avez-vous déjà vu' } },
          { stock: { offer_name: 'Avez-vous déjà vu' } },
          { stock: { offer_name: 'Avez-vous déjà vu' } },
          { stock: { offer_name: 'Avez-vous déjà vu' } },
          { stock: { offer_name: 'Avez-vous déjà vu' } },
          { stock: { offer_name: 'Avez-vous déjà vu' } },
        ],
        nbHitsPerPage: 5,
      }

      // When
      const wrapper = mount(<Table {...props} />)

      // Then
      const paginate = wrapper.find(Paginate)
      expect(paginate).toHaveLength(1)
      expect(paginate.props()).toStrictEqual({
        canNextPage: true,
        canPreviousPage: false,
        currentPage: 1,
        nbPages: 2,
        nextPage: expect.any(Function),
        previousPage: expect.any(Function),
      })
    })

    it('should render five bookings on page 1 & one booking on page 2 when clicking on next page', () => {
      // Given
      const props = {
        columns: [
          {
            headerTitle: 'Stock',
            accessor: 'stock',
            // eslint-disable-next-line react/display-name, react/no-multi-comp
            Cell: ({ value }) => <CellMock offer={value} />,
          },
        ],
        data: [
          { stock: { offer_name: 'Avez-vous déjà vu 1' } },
          { stock: { offer_name: 'Avez-vous déjà vu 2' } },
          { stock: { offer_name: 'Avez-vous déjà vu 3' } },
          { stock: { offer_name: 'Avez-vous déjà vu 4' } },
          { stock: { offer_name: 'Avez-vous déjà vu 5' } },
          { stock: { offer_name: 'Avez-vous déjà vu 6' } },
        ],
        nbHitsPerPage: 5,
      }

      // When
      const wrapper = mount(<Table {...props} />)

      // Then
      const paginate = wrapper.find(Paginate)
      const bookingsOnPageOne = wrapper.find('tbody').find('tr')
      expect(bookingsOnPageOne.at(0).text()).toBe('Avez-vous déjà vu 1')
      expect(bookingsOnPageOne.at(1).text()).toBe('Avez-vous déjà vu 2')
      expect(bookingsOnPageOne.at(2).text()).toBe('Avez-vous déjà vu 3')
      expect(bookingsOnPageOne.at(3).text()).toBe('Avez-vous déjà vu 4')
      expect(bookingsOnPageOne.at(4).text()).toBe('Avez-vous déjà vu 5')
      expect(bookingsOnPageOne).toHaveLength(5)

      // When
      const nextPageButton = paginate.find('button')
      nextPageButton.simulate('click')

      // Then
      const bookingsOnPageTwo = wrapper.find('tbody').find('tr')
      expect(bookingsOnPageTwo).toHaveLength(1)
      expect(bookingsOnPageTwo.at(0).text()).toBe('Avez-vous déjà vu 6')
    })
  })
})
