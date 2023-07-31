import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import * as reactTable from 'react-table'

import { BookingRecapResponseModel } from 'apiClient/v1'
import { Audience } from 'core/shared/types'

import TableWrapper from '../TableWrapper'

interface TestOffer {
  offer_name: string
}
const CellMock = ({
  offer: { offer_name: offerName },
}: {
  offer: TestOffer
}) => <span>{offerName}</span>

describe('TableWrapper', () => {
  it('should render a Table component with the right text', () => {
    const mockedValues = {
      canPreviousPage: true,
      canNextPage: true,
      getTableProps: vi.fn(() => ({})),
      getTableBodyProps: vi.fn(() => ({})),
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: vi.fn(() => <span>Offres</span>),
              getHeaderProps: vi.fn(),
              getSortByToggleProps: vi.fn(),
            },
            {
              id: 2,
              headerTitle: 'Beneficiaires',
              render: vi.fn(() => <span>Beneficiaires</span>),
              getHeaderProps: vi.fn(),
              getSortByToggleProps: vi.fn(),
            },
          ],
        },
      ],
      nextPage: vi.fn(),
      previousPage: vi.fn(),
      prepareRow: vi.fn(),
      page: [],
      pageCount: 1,
      state: {
        pageIndex: 0,
      },
    }
    const useTableSpy = vi
      .spyOn(reactTable, 'useTable')
      .mockImplementationOnce(
        () => mockedValues as unknown as reactTable.TableInstance<object>
      )
    const props = {
      columns: [
        {
          id: '1',
          headerTitle: 'Stock',
          accessor: 'bookingToken' as const,
          getHeaderProps: vi.fn(),
          getSortByToggleProps: vi.fn(),
        },
        {
          id: '2',
          headerTitle: 'Beneficiaire',
          accessor: 'bookingToken' as const,
          getHeaderProps: vi.fn(),
          getSortByToggleProps: vi.fn(),
        },
      ],
      currentPage: 0,
      data: [{} as BookingRecapResponseModel],
      nbBookings: 1,
      nbBookingsPerPage: 1,
      updateCurrentPage: vi.fn(),
      audience: Audience.INDIVIDUAL,
      bookingId: '1',
      reloadBookings: vi.fn(),
    }

    useTableSpy.mockReturnValue(
      mockedValues as unknown as reactTable.TableInstance<object>
    )

    render(<TableWrapper {...props} />)

    const headerCells = screen.getAllByRole('columnheader')
    expect(headerCells).toHaveLength(2)
    expect(headerCells[0]).toHaveTextContent('Offres')
    expect(headerCells[1]).toHaveTextContent('Beneficiaires')
  })

  it('should display the correct numbers of rows', () => {
    const props = {
      columns: [
        {
          id: '1',
          headerTitle: 'Stock',
          accessor: 'stock' as const,
          Cell: function ({ value }: { value: TestOffer }) {
            return <CellMock offer={value} />
          },
          getHeaderProps: vi.fn(),
          getSortByToggleProps: vi.fn(),
        },
        {
          id: '2',
          headerTitle: 'Beneficiaire',
          accessor: 'beneficiary' as const,
          Cell: function ({ value }: { value: TestOffer }) {
            return <CellMock offer={value} />
          },
          getHeaderProps: vi.fn(),
          getSortByToggleProps: vi.fn(),
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
      updateCurrentPage: vi.fn(),
      audience: Audience.INDIVIDUAL,
      bookingId: '1',
      reloadBookings: vi.fn(),
    }

    // @ts-expect-error we will remove react-table
    render(<TableWrapper {...props} />)

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(3)
  })

  describe('pagination', () => {
    it('should render a TablePagination component with the right props', () => {
      const props = {
        columns: [
          {
            id: '1',
            headerTitle: 'Stock',
            accessor: 'stock' as const,
            Cell: function ({ value }: { value: TestOffer }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: vi.fn(),
            getSortByToggleProps: vi.fn(),
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
        updateCurrentPage: vi.fn(),
        audience: Audience.INDIVIDUAL,
        bookingId: '1',
        reloadBookings: vi.fn(),
      }

      // @ts-expect-error we will remove react-table
      render(<TableWrapper {...props} />)

      expect(screen.getByText('Page 1/2')).toBeInTheDocument()
    })

    it('should render five bookings on page 1', () => {
      const props = {
        columns: [
          {
            id: '1',
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }: { value: TestOffer }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: vi.fn(),
            getSortByToggleProps: vi.fn(),
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
        updateCurrentPage: vi.fn(),
        audience: Audience.INDIVIDUAL,
        bookingId: '1',
        reloadBookings: vi.fn(),
      }

      // @ts-expect-error we will remove react-table
      render(<TableWrapper {...props} />)

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
      const props = {
        columns: [
          {
            id: '1',
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }: { value: TestOffer }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: vi.fn(),
            getSortByToggleProps: vi.fn(),
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
        updateCurrentPage: vi.fn(),
        audience: Audience.INDIVIDUAL,
        bookingId: '1',
        reloadBookings: vi.fn(),
      }
      // @ts-expect-error we will remove react-table
      render(<TableWrapper {...props} />)
      const nextButton = screen.getAllByRole('button')[2]

      await userEvent.click(nextButton)

      const bookingsOnPageTwo = screen.getAllByRole('row')
      expect(bookingsOnPageTwo).toHaveLength(2)
      const cells = screen.getAllByRole('cell')
      expect(cells[0]).toHaveTextContent('Avez-vous déjà vu 6')
      expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    })

    it('should go to previous when clicking on previous page button', async () => {
      const props = {
        columns: [
          {
            id: '1',
            headerTitle: 'Stock',
            accessor: 'stock',
            Cell: function ({ value }: { value: TestOffer }) {
              return <CellMock offer={value} />
            },
            getHeaderProps: vi.fn(),
            getSortByToggleProps: vi.fn(),
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
        updateCurrentPage: vi.fn(),
        audience: Audience.INDIVIDUAL,
        bookingId: '1',
        reloadBookings: vi.fn(),
      }
      // @ts-expect-error we will remove react-table
      render(<TableWrapper {...props} />)

      const previousPageButton = screen.getAllByRole('button')[1]
      await userEvent.click(previousPageButton)

      const bookingsOnPageTwo = screen.getAllByRole('row')
      expect(bookingsOnPageTwo).toHaveLength(6)
    })
  })
})
