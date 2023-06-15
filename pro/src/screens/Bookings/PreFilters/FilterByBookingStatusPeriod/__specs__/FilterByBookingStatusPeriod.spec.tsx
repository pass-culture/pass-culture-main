import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
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
  api: { getVenues: jest.fn() },
}))

const renderPreFilters = (props: PreFiltersProps) => {
  renderWithProviders(<PreFilters {...props} />)
}

describe('filter bookings by bookings period', () => {
  let props: PreFiltersProps

  beforeEach(() => {
    props = {
      appliedPreFilters: { ...DEFAULT_PRE_FILTERS },
      applyPreFilters: jest.fn(),
      venues: [getOfferVenueFactory()].map(({ id, name }) => ({
        id,
        displayName: name,
      })),
      getBookingsCSVFileAdapter: jest.fn(),
      getBookingsXLSFileAdapter: jest.fn(),
      hasResult: true,
      resetPreFilters: jest.fn(),
      isFiltersDisabled: false,
      isTableLoading: false,
      wereBookingsRequested: true,
      isLocalLoading: false,
    }
  })

  it('should select 30 days before today as period beginning date by default', () => {
    // When
    renderPreFilters(props)

    // Then
    expect(screen.getByDisplayValue('15/11/2020')).toBeInTheDocument()
  })

  it('should select today as period ending date by default', () => {
    // When
    renderPreFilters(props)

    // Then
    expect(screen.getByDisplayValue('15/12/2020')).toBeInTheDocument()
  })

  it('should allow to select period ending date before today', async () => {
    // Given
    renderPreFilters(props)
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    await userEvent.click(periodEndingDateInput)
    await userEvent.click(screen.getByText('14'))

    // Then
    expect(screen.getByDisplayValue('14/12/2020')).toBeInTheDocument()
  })

  it('should not allow to select period ending date after today', async () => {
    // Given
    renderPreFilters(props)

    // When
    const periodEndingDateInput = await screen.getByDisplayValue('15/12/2020')
    await userEvent.click(periodEndingDateInput)
    await userEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should not allow to select period ending date before selected beginning date', async () => {
    // Given
    renderPreFilters(props)
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    await userEvent.click(periodEndingDateInput)
    await userEvent.click(screen.getByLabelText('Previous Month'))
    await userEvent.click(screen.getByText('13'))

    // Then
    expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
  })

  it('should allow to select period beginning date before selected ending date', async () => {
    // Given
    renderPreFilters(props)
    const periodBeginningDateInput = screen.getByDisplayValue('15/11/2020')

    // When
    await userEvent.click(periodBeginningDateInput)
    await userEvent.click(screen.getByText('14'))

    // Then
    expect(screen.getByDisplayValue('14/11/2020')).toBeInTheDocument()
  })

  it('should not allow to select period beginning date after ending date', async () => {
    // Given
    renderPreFilters(props)

    // When
    const periodBeginningDateInput = screen.getByDisplayValue('15/11/2020')
    await userEvent.click(periodBeginningDateInput)
    await userEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should select booked status as booking status filter by default', () => {
    // Given
    renderPreFilters(props)

    // Then
    expect(
      screen.queryByDisplayValue('Période de réservation')
    ).toBeInTheDocument()
  })

  it('should allow to select booking status filter', async () => {
    // Given
    renderPreFilters(props)
    const bookingStatusFilterInput = screen.getByDisplayValue(
      'Période de réservation'
    )

    // When
    await userEvent.click(bookingStatusFilterInput)
    await userEvent.click(screen.getByText('Période de validation'))

    // Then
    expect(screen.queryByText('Période de validation')).toBeInTheDocument()
  })
})
