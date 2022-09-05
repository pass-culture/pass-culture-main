import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import * as reactTable from 'react-table'

import TableWrapper from '../TableWrapper'

const CellMock = ({ offer: { offer_name: offerName } }) => (
  <span>{offerName}</span>
)

describe('components | TableWrapper', () => {
  it('should render a Table component with the right text', () => {
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
    render(<TableWrapper {...props} />)

    // Then
    const headerCells = screen.getAllByRole('columnheader')
    expect(headerCells).toHaveLength(2)
    expect(headerCells[0]).toHaveTextContent('Offres')
    expect(headerCells[1]).toHaveTextContent('Beneficiaires')
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
    render(<TableWrapper {...props} />)

    // Then
    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(3)
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
      render(<TableWrapper {...props} />)

      // Then
      expect(screen.getByText('Page 1/2')).toBeInTheDocument()
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
      render(<TableWrapper {...props} />)

      // Then
      const bookingsOnPageOne = screen.getAllByRole('row')
      expect(bookingsOnPageOne).toHaveLength(6)
      const cells = screen.getAllByRole('cell')
      expect(cells[0]).toHaveTextContent('Avez-vous déjà vu 1')
      expect(cells[1]).toHaveTextContent('Avez-vous déjà vu 2')
      expect(cells[2]).toHaveTextContent('Avez-vous déjà vu 3')
      expect(cells[3]).toHaveTextContent('Avez-vous déjà vu 4')
      expect(cells[4]).toHaveTextContent('Avez-vous déjà vu 5')
    })

    it('should render one booking on page 2 when clicking on next page', async () => {
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
      render(<TableWrapper {...props} />)
      const nextButton = screen.getAllByRole('button')[2]

      // When
      await userEvent.click(nextButton)

      // Then
      const bookingsOnPageTwo = screen.getAllByRole('row')
      expect(bookingsOnPageTwo).toHaveLength(2)
      const cells = screen.getAllByRole('cell')
      expect(cells[0]).toHaveTextContent('Avez-vous déjà vu 6')
      expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    })

    it('should go to previous when clicking on previous page button', async () => {
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
      render(<TableWrapper {...props} />)

      // When
      const previousPageButton = screen.getAllByRole('button')[1]
      await userEvent.click(previousPageButton)

      // Then
      const bookingsOnPageTwo = screen.getAllByRole('row')
      expect(bookingsOnPageTwo).toHaveLength(6)
    })
  })
})
