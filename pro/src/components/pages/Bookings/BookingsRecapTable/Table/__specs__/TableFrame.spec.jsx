import { mount } from 'enzyme'
import React from 'react'
import * as reactTable from 'react-table'

import TableHead from '../Head/TableHead'
import TablePagination from '../Paginate/TablePagination'
import TableFrame from '../TableFrame'

const CellMock = ({ offer: { offer_name: offerName } }) => (
  <span>{offerName}</span>
)

describe('components | TableFrame', () => {
  it('should render a TableHead component with the right props', () => {
    // Given
    const mockedValues = {
      canPreviousPage: true,
      canNextPage: true,
      getTableProps: jest.fn(() => ({})),
      getTableBodyProps: jest.fn(() => ({})),
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
            },
            {
              id: 2,
              headerTitle: 'Beneficiaires',
              render: jest.fn(() => <span>Beneficiaires</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
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
    const useTableSpy = jest
      .spyOn(reactTable, 'useTable')
      .mockImplementationOnce(() => mockedValues)
    const props = {
      columns: [
        {
          id: 1,
          headerTitle: 'Stock',
          accessor: 'stock',
          getHeaderProps: jest.fn(),
          getSortByToggleProps: jest.fn(),
        },
        {
          id: 2,
          headerTitle: 'Beneficiaire',
          accessor: 'beneficiary',
          getHeaderProps: jest.fn(),
          getSortByToggleProps: jest.fn(),
        },
      ],
      currentPage: 0,
      data: [{}],
      nbBookings: 1,
      nbBookingsPerPage: 1,
      updateCurrentPage: jest.fn(),
    }

    useTableSpy.mockReturnValue(mockedValues)

    // When
    const table = mount(<TableFrame {...props} />)

    // Then
    const tableHead = table.find(TableHead)
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
          id: 1,
          headerTitle: 'Stock',
          accessor: 'stock',
          Cell: function ({ value }) {
            return <CellMock offer={value} />
          },
          getHeaderProps: jest.fn(),
          getSortByToggleProps: jest.fn(),
        },
        {
          id: 2,
          headerTitle: 'Beneficiaire',
          accessor: 'beneficiary',
          Cell: function ({ value }) {
            return <CellMock offer={value} />
          },
          getHeaderProps: jest.fn(),
          getSortByToggleProps: jest.fn(),
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
      nbBookings: 2,
      nbBookingsPerPage: 2,
      currentPage: 0,
      updateCurrentPage: jest.fn(),
    }

    // When
    const table = mount(<TableFrame {...props} />)

    // Then
    const tableRowsNumber = table.find('tbody > tr').length
    expect(tableRowsNumber).toBe(2)
  })

  describe('pagination', () => {
    it('should render a TablePagination component with the right props', () => {
      // Given
      const props = {
        columns: [
          {
            id: 1,
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: jest.fn(),
            getSortByToggleProps: jest.fn(),
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
        nbBookings: 6,
        nbBookingsPerPage: 5,
        currentPage: 0,
        updateCurrentPage: jest.fn(),
      }

      // When
      const wrapper = mount(<TableFrame {...props} />)

      // Then
      const paginate = wrapper.find(TablePagination)
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

    it('should render five bookings on page 1', () => {
      // Given
      const props = {
        columns: [
          {
            id: 1,
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: jest.fn(),
            getSortByToggleProps: jest.fn(),
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
        nbBookings: 6,
        nbBookingsPerPage: 5,
        currentPage: 0,
        updateCurrentPage: jest.fn(),
      }

      // When
      const wrapper = mount(<TableFrame {...props} />)

      // Then
      const bookingsOnPageOne = wrapper.find('tbody').find('tr')
      expect(bookingsOnPageOne.at(0).text()).toBe('Avez-vous déjà vu 1')
      expect(bookingsOnPageOne.at(1).text()).toBe('Avez-vous déjà vu 2')
      expect(bookingsOnPageOne.at(2).text()).toBe('Avez-vous déjà vu 3')
      expect(bookingsOnPageOne.at(3).text()).toBe('Avez-vous déjà vu 4')
      expect(bookingsOnPageOne.at(4).text()).toBe('Avez-vous déjà vu 5')
      expect(bookingsOnPageOne).toHaveLength(5)
    })

    it('should render one booking on page 2 when clicking on next page', () => {
      // Given
      const props = {
        columns: [
          {
            id: 1,
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: jest.fn(),
            getSortByToggleProps: jest.fn(),
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
        nbBookings: 6,
        nbBookingsPerPage: 5,
        currentPage: 0,
        updateCurrentPage: jest.fn(),
      }
      const wrapper = mount(<TableFrame {...props} />)
      const paginate = wrapper.find(TablePagination)
      const nextPageButton = paginate.find('button').at(1)

      // When
      nextPageButton.simulate('click')

      // Then
      const bookingsOnPageTwo = wrapper.find('tbody').find('tr')
      expect(bookingsOnPageTwo).toHaveLength(1)
      expect(bookingsOnPageTwo.at(0).text()).toBe('Avez-vous déjà vu 6')
      expect(props.updateCurrentPage).toHaveBeenCalledTimes(1)
      expect(props.updateCurrentPage).toHaveBeenCalledWith(1)
    })

    it('should go to previous when clicking on previous page button', () => {
      // Given
      const props = {
        columns: [
          {
            id: 1,
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: jest.fn(),
            getSortByToggleProps: jest.fn(),
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
        nbBookings: 6,
        nbBookingsPerPage: 5,
        currentPage: 1,
        updateCurrentPage: jest.fn(),
      }
      const wrapper = mount(<TableFrame {...props} />)
      const paginate = wrapper.find(TablePagination)

      // When
      const previousPageButton = paginate.find('button').at(0)
      previousPageButton.simulate('click')

      // Then
      expect(props.updateCurrentPage).toHaveBeenNthCalledWith(1, 0)
    })
  })
})
