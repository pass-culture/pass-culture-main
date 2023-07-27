import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { getOfferVenueFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import PreFilters, { PreFiltersProps } from '../../PreFilters'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('apiClient/api', () => ({
  api: { getVenues: vi.fn() },
}))

const renderPreFilters = (props: PreFiltersProps) => {
  renderWithProviders(<PreFilters {...props} />)
}

describe('filter bookings by bookings period', () => {
  let props: PreFiltersProps

  beforeEach(() => {
    props = {
      appliedPreFilters: { ...DEFAULT_PRE_FILTERS },
      applyPreFilters: vi.fn(),
      venues: [getOfferVenueFactory()].map(({ id, name }) => ({
        id: id.toString(),
        displayName: name,
      })),
      getBookingsCSVFileAdapter: vi.fn(),
      getBookingsXLSFileAdapter: vi.fn(),
      hasResult: true,
      resetPreFilters: vi.fn(),
      isFiltersDisabled: false,
      isTableLoading: false,
      wereBookingsRequested: true,
      isLocalLoading: false,
    }
  })

  it('should select 30 days before today as period beginning date by default', () => {
    renderPreFilters(props)

    expect(screen.getByLabelText('Début de la période')).toHaveValue(
      '2020-11-15'
    )
  })

  it('should select today as period ending date by default', () => {
    renderPreFilters(props)

    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-12-15')
  })

  it('should select booked status as booking status filter by default', () => {
    renderPreFilters(props)

    expect(
      screen.queryByDisplayValue('Période de réservation')
    ).toBeInTheDocument()
  })

  it('should allow to select booking status filter', async () => {
    renderPreFilters(props)
    const bookingStatusFilterInput = screen.getByDisplayValue(
      'Période de réservation'
    )

    await userEvent.click(bookingStatusFilterInput)
    await userEvent.click(screen.getByText('Période de validation'))

    expect(screen.queryByText('Période de validation')).toBeInTheDocument()
  })
})
