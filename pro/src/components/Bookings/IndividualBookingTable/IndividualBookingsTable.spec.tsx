import { screen } from '@testing-library/react'

import {
  bookingRecapFactory,
  bookingRecapStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualBookingsTable,
  type IndividualBookingsTableProps,
} from './IndividualBookingsTable'

const renderIndividualBookingTable = (props: IndividualBookingsTableProps) =>
  renderWithProviders(<IndividualBookingsTable {...props} />)

describe('IndividualBookingsTable', () => {
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
      isLoading: false,
    }

    renderIndividualBookingTable(props)

    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })

  it('should render the no-result state with subtitle and reset action when there are no bookings', () => {
    const props: IndividualBookingsTableProps = {
      bookings: [],
      bookingStatuses: [],
      updateGlobalFilters: vi.fn(),
      resetFilters: vi.fn(),
      isLoading: false,
    }

    renderIndividualBookingTable(props)

    expect(
      screen.getByText('Aucune réservation trouvée pour votre recherche')
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou',
        { exact: false }
      )
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Afficher toutes les réservations' })
    ).toBeInTheDocument()
  })
})
