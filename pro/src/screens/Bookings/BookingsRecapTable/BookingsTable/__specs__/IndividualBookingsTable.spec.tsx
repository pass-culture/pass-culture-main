import { screen } from '@testing-library/react'
import React from 'react'

import {
  GetIndividualOfferFactory,
  bookingRecapFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualBookingsTable,
  IndividualBookingsTableProps,
} from '../IndividualBookingsTable'

const renderIndividualBookingTable = (props: IndividualBookingsTableProps) =>
  renderWithProviders(<IndividualBookingsTable {...props} />)

describe('CollectiveTableRow', () => {
  it('should render a table with bookings', () => {
    const offer = GetIndividualOfferFactory({ name: 'Offre de test' })

    const props: IndividualBookingsTableProps = {
      bookings: [
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
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
