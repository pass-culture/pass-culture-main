import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualBookingsTable,
  type IndividualBookingsTableProps,
} from '../../IndividualBookingTable/IndividualBookingsTable'

const renderIndividualBookingTable = (props: IndividualBookingsTableProps) =>
  renderWithProviders(<IndividualBookingsTable {...props} />)

describe('CollectiveTableRow', () => {
  it('should render a table with bookings', () => {
    const props: IndividualBookingsTableProps = {
      bookings: [
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: 'Offre de test' }),
        }),
      ],
      bookingStatuses: [],
      updateGlobalFilters: vi.fn(),
      resetFilters: vi.fn(),
    }

    renderIndividualBookingTable(props)

    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })

  it('should render message to empty the filters when no bookings', () => {
    const props: IndividualBookingsTableProps = {
      bookings: [],
      bookingStatuses: [],
      updateGlobalFilters: vi.fn(),
      resetFilters: vi.fn(),
    }

    renderIndividualBookingTable(props)

    expect(
      screen.queryByText('Aucune réservation trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('goes back to page 1 when the bookings list changes', async () => {
    // Start with 25 (2 pages), go to page 2, then rerender with 5
    const many = Array.from({ length: 25 }, (_, i) =>
      bookingRecapFactory({
        stock: bookingRecapStockFactory({ offerName: `Offre ${i + 1}` }),
      })
    )
    const few = Array.from({ length: 5 }, (_, i) =>
      bookingRecapFactory({
        stock: bookingRecapStockFactory({ offerName: `Mini ${i + 1}` }),
      })
    )

    const props: IndividualBookingsTableProps = {
      bookings: many,
      bookingStatuses: [],
      updateGlobalFilters: vi.fn(),
      resetFilters: vi.fn(),
    }

    const { rerender } = renderWithProviders(
      <IndividualBookingsTable {...props} />
    )

    // Go to page 2
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(screen.getAllByRole('link', { name: /Offre \d+/ })).toHaveLength(5) // last 5

    // Now shrink the list and rerender
    rerender(<IndividualBookingsTable {...props} bookings={few} />)

    // Back to page 1 showing the new 5
    expect(screen.getAllByRole('link', { name: /Mini \d+/ })).toHaveLength(5)
    // And only one page, so next is disabled
    expect(
      screen.queryByRole('button', { name: 'Page suivante' })
    ).not.toBeInTheDocument()
  })

  const renderIndividualBookingTable = (props: IndividualBookingsTableProps) =>
    renderWithProviders(<IndividualBookingsTable {...props} />)

  describe('IndividualBookingsTable – extra cases', () => {
    it('paginates 20 bookings per page and shows the next page', async () => {
      // 25 bookings to force 2 pages (20 + 5)
      const bookings = Array.from({ length: 25 }, (_, i) =>
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: `Offre ${i + 1}` }),
        })
      )

      const props: IndividualBookingsTableProps = {
        bookings,
        bookingStatuses: [],
        updateGlobalFilters: vi.fn(),
        resetFilters: vi.fn(),
      }

      renderIndividualBookingTable(props)

      // Page 1 shows first 20 links
      expect(screen.getAllByRole('link', { name: /Offre \d+/ })).toHaveLength(
        20
      )
      expect(screen.getByRole('link', { name: 'Offre 1' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Offre 20' })).toBeInTheDocument()

      // Go to next page
      const next = screen.getByRole('button', { name: 'Page suivante' })
      await userEvent.click(next)

      // Page 2 shows remaining 5
      expect(screen.getAllByRole('link', { name: /Offre \d+/ })).toHaveLength(5)
      expect(screen.getByRole('link', { name: 'Offre 21' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Offre 25' })).toBeInTheDocument()
    })

    it('disables previous/next when there is only one page', () => {
      // 3 bookings => single page
      const bookings = [1, 2, 3].map((i) =>
        bookingRecapFactory({
          stock: bookingRecapStockFactory({ offerName: `Offre ${i}` }),
        })
      )

      const props: IndividualBookingsTableProps = {
        bookings,
        bookingStatuses: [],
        updateGlobalFilters: vi.fn(),
        resetFilters: vi.fn(),
      }

      renderIndividualBookingTable(props)

      const prev = screen.queryByRole('button', { name: 'Page précédente' })
      const next = screen.queryByRole('button', { name: 'Page suivante' })

      expect(prev).not.toBeInTheDocument()
      expect(next).not.toBeInTheDocument()
    })

    it('resets to page 1 when no result and clicking "Afficher toutes les réservations"', async () => {
      const resetFilters = vi.fn()
      const props: IndividualBookingsTableProps = {
        bookings: [],
        bookingStatuses: [],
        updateGlobalFilters: vi.fn(),
        resetFilters,
      }

      renderIndividualBookingTable(props)

      // No-result banner + reset CTA come from the Table props
      expect(
        screen.getByText('Aucune réservation trouvée pour votre recherche')
      ).toBeInTheDocument()
      const resetBtn = screen.getByRole('button', {
        name: 'Afficher toutes les réservations',
      })
      await userEvent.click(resetBtn)
      expect(resetFilters).toHaveBeenCalledTimes(1)
    })
  })
})
