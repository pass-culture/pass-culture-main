import '@testing-library/jest-dom'

import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import type { Store } from 'redux'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import { configureTestStore } from 'store/testUtils'
import { venueFactory } from 'utils/apiFactories'

import PreFilters, { IPreFiltersProps } from '../../PreFilters'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
}))

const renderPreFilters = (props: IPreFiltersProps, store: Store) => {
  return render(
    <Provider store={store}>
      <PreFilters {...props} />
    </Provider>
  )
}

describe('filter bookings by bookings period', () => {
  let props: IPreFiltersProps
  let store: Store
  beforeEach(() => {
    props = {
      appliedPreFilters: { ...DEFAULT_PRE_FILTERS },
      applyPreFilters: jest.fn(),
      venues: [venueFactory()].map(({ id, name }) => ({
        id,
        displayName: name,
      })),
      getBookingsCSVFileAdapter: jest.fn(),
      getBookingsXLSFileAdapter: jest.fn(),
      isBookingFiltersActive: true,
      hasResult: true,
      resetPreFilters: jest.fn(),
      isFiltersDisabled: false,
      isTableLoading: false,
      wereBookingsRequested: true,
      isLocalLoading: false,
    }

    store = configureTestStore()
  })

  it('should select 30 days before today as period beginning date by default', async () => {
    // When
    renderPreFilters(props, store)

    // Then
    await expect(
      screen.findByDisplayValue('15/11/2020')
    ).resolves.toBeInTheDocument()
  })

  it('should select today as period ending date by default', async () => {
    // When
    renderPreFilters(props, store)

    // Then
    await expect(
      screen.findByDisplayValue('15/12/2020')
    ).resolves.toBeInTheDocument()
  })

  it('should allow to select period ending date before today', async () => {
    // Given
    renderPreFilters(props, store)
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByText('14'))

    // Then
    await expect(
      screen.findByDisplayValue('14/12/2020')
    ).resolves.toBeInTheDocument()
  })

  it('should not allow to select period ending date after today', async () => {
    // Given
    renderPreFilters(props, store)

    // When
    const periodEndingDateInput = await screen.findByDisplayValue('15/12/2020')
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should not allow to select period ending date before selected beginning date', async () => {
    // Given
    renderPreFilters(props, store)
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByLabelText('Previous Month'))
    fireEvent.click(screen.getByText('13'))

    // Then
    expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
  })

  it('should allow to select period beginning date before selected ending date', async () => {
    // Given
    renderPreFilters(props, store)
    const periodBeginningDateInput = screen.getByDisplayValue('15/11/2020')

    // When
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('14'))

    // Then
    await expect(
      screen.findByDisplayValue('14/11/2020')
    ).resolves.toBeInTheDocument()
  })

  it('should not allow to select period beginning date after ending date', async () => {
    // Given
    renderPreFilters(props, store)

    // When
    const periodBeginningDateInput = screen.getByDisplayValue('15/11/2020')
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should select booked status as booking status filter by default', async () => {
    props.isBookingFiltersActive = true
    // Given
    renderPreFilters(props, store)

    // Then
    expect(
      screen.queryByDisplayValue('Période de réservation')
    ).toBeInTheDocument()
  })

  it('should allow to select booking status filter', async () => {
    props.isBookingFiltersActive = true
    // Given
    renderPreFilters(props, store)
    const bookingStatusFilterInput = screen.getByDisplayValue(
      'Période de réservation'
    )

    // When
    fireEvent.click(bookingStatusFilterInput)
    fireEvent.click(screen.getByText('Période de validation'))

    // Then
    expect(screen.queryByText('Période de validation')).toBeInTheDocument()
  })
})
