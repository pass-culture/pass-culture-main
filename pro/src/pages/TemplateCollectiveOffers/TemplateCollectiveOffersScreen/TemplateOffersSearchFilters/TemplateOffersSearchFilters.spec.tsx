import { screen, waitFor } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { TemplateOffersSearchFilters } from './TemplateOffersSearchFilters'

describe('TemplateOffersSearchFilters', () => {
  it('should render without accessibility violations', async () => {
    vi.spyOn(api, 'getVenueAddresses').mockResolvedValue([])

    const { container } = renderWithProviders(
      <TemplateOffersSearchFilters
        hasFilters={false}
        applyFilters={() => vi.fn()}
        setSelectedFilters={() => vi.fn()}
        disableAllFilters={false}
        resetFilters={() => vi.fn()}
        offererId="1"
        selectedFilters={{
          name: '',
          offererId: '',
          venueId: '',
          format: 'all',
          status: [],
          periodBeginningDate: '',
          periodEndingDate: '',
          locationType: undefined,
          offererAddressId: undefined,
          page: undefined,
        }}
      />,
      {
        storeOverrides: {
          user: {
            selectedPartnerVenue: { id: 1 },
          },
        },
      }
    )

    await waitFor(() => {
      expect(api.getVenueAddresses).toHaveBeenCalled()
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render filters correctly', () => {
    renderWithProviders(
      <TemplateOffersSearchFilters
        hasFilters={false}
        applyFilters={() => vi.fn()}
        setSelectedFilters={() => vi.fn()}
        disableAllFilters={false}
        resetFilters={() => vi.fn()}
        offererId="1"
        selectedFilters={{
          name: '',
          offererId: '',
          venueId: '',
          format: 'all',
          status: [],
          periodBeginningDate: '',
          periodEndingDate: '',
          locationType: undefined,
          offererAddressId: undefined,
          page: undefined,
        }}
      />,
      {
        storeOverrides: {
          user: {
            selectedPartnerVenue: { id: 1 },
          },
        },
      }
    )
    expect(screen.getByLabelText('Nom de l’offre')).toBeInTheDocument()
    expect(screen.getByLabelText('Statut')).toBeInTheDocument()
    expect(screen.getByLabelText('Format')).toBeInTheDocument()
    expect(screen.getByLabelText('Date de début')).toBeInTheDocument()
    expect(screen.getByLabelText('Date de fin')).toBeInTheDocument()
  })
})
