import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { Audience } from 'core/shared/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PreFilters, PreFiltersProps } from '../PreFilters'

const mockUpdateUrl = vi.fn()

vi.mock('utils/date', async () => {
  return {
    ...(await vi.importActual('utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

vi.mock('apiClient/api', () => ({
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
      audience: Audience.INDIVIDUAL,
      venues: [
        {
          id: '12',
          displayName: 'Mon nom de lieu',
        },
      ],
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

    const offerVenuIdInput = screen.getByLabelText('Lieu')
    await userEvent.selectOptions(offerVenuIdInput, '12')

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
      offerVenueId: '12',
    })
  })
})
