import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useState } from 'react'

import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PreFilters, type PreFiltersProps } from './PreFilters'

const mockApplyNow = vi.fn()

vi.mock('@/commons/utils/date', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('@/apiClient/api', () => ({
  api: { getVenues: vi.fn() },
}))

/**
 * Harness to control selectedPreFilters from the test and
 * to capture the final payload when the user clicks "Afficher".
 */
const renderPreFilters = (
  incomingProps: PreFiltersProps,
  features: string[] = []
) => {
  const Harness = () => {
    const [selected, setSelected] = useState({
      ...incomingProps.selectedPreFilters,
    })

    const updateSelectedFilters = (updated: Partial<typeof selected>) => {
      setSelected((prev) => ({ ...prev, ...updated }))
    }

    const applyNow = () => {
      mockApplyNow({ ...selected })
      // also call the provided prop to keep compatibility if needed
      incomingProps.applyNow()
    }

    return (
      <PreFilters
        {...incomingProps}
        selectedPreFilters={selected}
        updateSelectedFilters={updateSelectedFilters}
        applyNow={applyNow}
      />
    )
  }

  renderWithProviders(<Harness />, { features })
}

describe('filter bookings by bookings period', () => {
  let props: PreFiltersProps

  beforeEach(() => {
    mockApplyNow.mockReset()

    props = {
      offererAddresses: [{ value: '21', label: 'label - street city cp' }],
      hasResult: true,
      resetPreFilters: vi.fn(),
      isFiltersDisabled: false,
      isTableLoading: false,
      wereBookingsRequested: true,
      isLocalLoading: false,
      updateUrl: vi.fn(),

      selectedPreFilters: { ...DEFAULT_PRE_FILTERS },
      updateSelectedFilters: vi.fn(),
      hasPreFilters: false,
      isRefreshRequired: false,
      applyNow: vi.fn(),
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

  it('should allow to select booking status filter', async () => {
    renderPreFilters(props)
    const bookingStatusFilterInput = screen.getByDisplayValue(
      'Période de réservation'
    )

    await userEvent.click(bookingStatusFilterInput)
    await userEvent.click(screen.getByText('Période de validation'))

    expect(screen.queryByText('Période de validation')).toBeInTheDocument()
  })

  it('should filter with a combination of filters', async () => {
    renderPreFilters(props)

    const offerEventDateInput = screen.getByLabelText('Date de l’évènement')
    await userEvent.clear(offerEventDateInput)
    await userEvent.type(offerEventDateInput, '2020-12-13')

    const offererAddressInput = screen.getByLabelText('Localisation')
    await userEvent.selectOptions(offererAddressInput, '21')

    const periodBeginningDateInput = screen.getByLabelText(
      'Début de la période'
    )
    const periodEndingDateInput = screen.getByLabelText('Fin de la période')

    await userEvent.clear(periodBeginningDateInput)
    await userEvent.type(periodBeginningDateInput, '2020-12-01')

    await userEvent.clear(periodEndingDateInput)
    await userEvent.type(periodEndingDateInput, '2020-12-02')

    const select = screen.getByLabelText('Type de période')
    await userEvent.selectOptions(select, 'reimbursed')

    await userEvent.click(screen.getByText('Afficher'))

    expect(mockApplyNow).toHaveBeenCalledWith({
      bookingBeginningDate: '2020-12-01',
      bookingEndingDate: '2020-12-02',
      bookingStatusFilter: 'reimbursed',
      offerEventDate: '2020-12-13',
      offerId: DEFAULT_PRE_FILTERS.offerId,
      offerVenueId: DEFAULT_PRE_FILTERS.offerVenueId,
      offererAddressId: '21',
      offererId: DEFAULT_PRE_FILTERS.offererId,
    })
  })

  it('should be able to filter by offererAddress', async () => {
    renderPreFilters(props)

    const offererAddressInput = screen.getByLabelText('Localisation')
    await userEvent.selectOptions(offererAddressInput, '21')

    await userEvent.click(screen.getByText('Afficher'))

    expect(mockApplyNow).toHaveBeenCalledWith({
      bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
      bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
      bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
      offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
      offerId: DEFAULT_PRE_FILTERS.offerId,
      offerVenueId: DEFAULT_PRE_FILTERS.offerVenueId,
      offererAddressId: '21',
      offererId: DEFAULT_PRE_FILTERS.offererId,
    })
  })

  it('should disable reset button when there are no prefilters', () => {
    renderPreFilters({ ...props, hasPreFilters: false })

    const resetButton = screen.getByRole('button', {
      name: /réinitialiser les filtres/i,
    })
    expect(resetButton).toBeDisabled()
  })

  it('should enable reset button when there are prefilters and call resetPreFilters', async () => {
    const resetPreFilters = vi.fn()
    renderPreFilters({ ...props, hasPreFilters: true, resetPreFilters })

    const resetButton = screen.getByRole('button', {
      name: /réinitialiser les filtres/i,
    })
    expect(resetButton).toBeEnabled()

    await userEvent.click(resetButton)
    expect(resetPreFilters).toHaveBeenCalledTimes(1)
  })

  it('should display refresh-required message when isRefreshRequired is true', () => {
    renderPreFilters({ ...props, isRefreshRequired: true })

    expect(screen.getByTestId('refresh-required-message')).toBeInTheDocument()
  })

  it('should not display refresh-required message when isRefreshRequired is false', () => {
    renderPreFilters({ ...props, isRefreshRequired: false })

    expect(
      screen.queryByTestId('refresh-required-message')
    ).not.toBeInTheDocument()
  })

  it('should disable "Afficher" when table is loading', () => {
    renderPreFilters({ ...props, isTableLoading: true })

    expect(screen.getByRole('button', { name: 'Afficher' })).toBeDisabled()
  })

  it('should disable "Afficher" when local loading', () => {
    renderPreFilters({ ...props, isLocalLoading: true })

    expect(screen.getByRole('button', { name: 'Afficher' })).toBeDisabled()
  })

  it('should disable "Afficher" when filters are disabled', () => {
    renderPreFilters({ ...props, isFiltersDisabled: true })

    expect(screen.getByRole('button', { name: 'Afficher' })).toBeDisabled()
  })

  it('should reset offerEventDate to default when event date is cleared', async () => {
    renderPreFilters(props)

    const offerEventDateInput = screen.getByLabelText('Date de l’évènement')

    await userEvent.clear(offerEventDateInput)
    await userEvent.type(offerEventDateInput, '2020-12-13')

    await userEvent.clear(offerEventDateInput)

    await userEvent.click(screen.getByText('Afficher'))

    expect(mockApplyNow).toHaveBeenCalledWith(
      expect.objectContaining({
        offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
      })
    )
  })

  describe('download buttons feature toggle', () => {
    it('should show MultiDownloadButtonsModal when WIP_SWITCH_VENUE feature is disabled', () => {
      renderPreFilters(props, [])

      expect(
        screen.getByRole('button', { name: 'Télécharger' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Où les télécharger ?' })
      ).not.toBeInTheDocument()
    })

    it('should show MovedBookingDownloadWarningModal when WIP_SWITCH_VENUE feature is enabled', () => {
      renderPreFilters(props, ['WIP_SWITCH_VENUE'])

      expect(
        screen.getByRole('button', { name: 'Où les télécharger ?' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Télécharger' })
      ).not.toBeInTheDocument()
    })
  })
})
