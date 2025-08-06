import { screen } from '@testing-library/react'

import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualBookingsTable,
  IndividualBookingsTableProps,
} from '../IndividualBookingsTable'

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
})
