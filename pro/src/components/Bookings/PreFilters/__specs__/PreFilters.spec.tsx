import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { Audience } from '@/commons/core/shared/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PreFilters, PreFiltersProps } from '../PreFilters'

const mockUpdateUrl = vi.fn()

vi.mock('@/commons/utils/date', async () => {
  return {
    ...(await vi.importActual('@/commons/utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('@/apiClient//api', () => ({
  api: { getVenues: vi.fn() },
}))

const renderPreFilters = (props: PreFiltersProps, features: string[] = []) => {
  renderWithProviders(<PreFilters {...props} />, {
    features,
  })
}

describe('filter bookings by bookings period', () => {
  let props: PreFiltersProps

  beforeEach(() => {
    props = {
      appliedPreFilters: { ...DEFAULT_PRE_FILTERS },
      applyPreFilters: vi.fn(),
      audience: Audience.INDIVIDUAL,
      venues: [
        {
          id: '12',
          displayName: 'Mon nom de lieu',
        },
      ],
      offererAddresses: [{ value: '21', label: 'label - street city cp' }],
      hasResult: true,
      resetPreFilters: vi.fn(),
      isFiltersDisabled: false,
      isTableLoading: false,
      wereBookingsRequested: true,
      isLocalLoading: false,
      updateUrl: mockUpdateUrl,
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

    const offerVenuIdInput = screen.getByLabelText('Localisation')
    await userEvent.selectOptions(offerVenuIdInput, '21')

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
    expect(mockUpdateUrl).toHaveBeenCalledWith({
      bookingBeginningDate: '2020-12-01',
      bookingEndingDate: '2020-12-02',
      bookingStatusFilter: 'reimbursed',
      offerEventDate: '2020-12-13',
      offerId: undefined,
      offerVenueId: 'all',
      offererAddressId: '21',
      offererId: 'all',
    })
  })

  it('should be able to filter by offererAddress', async () => {
    renderPreFilters(props)

    const offerVenuIdInput = screen.getByLabelText('Localisation')
    await userEvent.selectOptions(offerVenuIdInput, '21')

    await userEvent.click(screen.getByText('Afficher'))
    expect(mockUpdateUrl).toHaveBeenCalledWith({
      bookingBeginningDate: DEFAULT_PRE_FILTERS.bookingBeginningDate,
      bookingEndingDate: DEFAULT_PRE_FILTERS.bookingEndingDate,
      bookingStatusFilter: DEFAULT_PRE_FILTERS.bookingStatusFilter,
      offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
      offerId: DEFAULT_PRE_FILTERS.offerId,
      offerVenueId: DEFAULT_PRE_FILTERS.offerVenueId,
      offererAddressId: '21',
      offererId: 'all',
    })
  })

  it('should not display offererAddress for collective audiance', () => {
    props.audience = Audience.COLLECTIVE
    renderPreFilters(props)

    expect(screen.queryByLabelText('Localisation')).not.toBeInTheDocument()
  })
})
