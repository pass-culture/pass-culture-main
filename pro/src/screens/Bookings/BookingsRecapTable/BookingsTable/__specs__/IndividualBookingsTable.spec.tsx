import { screen } from '@testing-library/react'
import React from 'react'

import { bookingRecapFactory } from 'utils/apiFactories'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  IndividualBookingsTable,
  IndividualBookingsTableProps,
} from '../IndividualBookingsTable'

const renderIndividualBookingTable = (props: IndividualBookingsTableProps) =>
  renderWithProviders(<IndividualBookingsTable {...props} />)

describe('CollectiveTableRow', () => {
  it('should render a table with bookings', () => {
    const offer = individualOfferFactory({ name: 'Offre de test' })

    const props: IndividualBookingsTableProps = {
      bookings: [
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
      ],
      bookingStatuses: [],
      updateGlobalFilters: jest.fn(),
    }

    renderIndividualBookingTable(props)

    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })

  it('should render empty state when no bookings', async () => {
    const props: IndividualBookingsTableProps = {
      bookings: [],
      bookingStatuses: [],
      updateGlobalFilters: jest.fn(),
    }

    renderIndividualBookingTable(props)

    expect(
      screen.queryByText('Vous n’avez pas encore de réservations')
    ).toBeInTheDocument()
  })
})
