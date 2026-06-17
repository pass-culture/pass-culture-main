import { screen, waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import type { VenueProviderResponse } from '@/apiClient/v1/new'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SynchronizationConnexions } from './SynchronizationConnexions'

vi.mock('../VenueProviderList/VenueProviderCard', () => ({
  VenueProviderCard: ({
    venueProvider,
  }: {
    venueProvider: VenueProviderResponse
  }) => (
    <div data-testid="venue-provider-card">{venueProvider.provider.name}</div>
  ),
}))

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getProvidersByVenue: vi.fn(),
  },
}))

const renderSynchronizationConnexions = async (
  venueProviders: VenueProviderResponse[] = []
) => {
  renderWithProviders(
    <SynchronizationConnexions
      venue={defaultGetVenue}
      venueProviders={venueProviders}
    />
  )

  await waitFor(() => {
    expect(screen.getByText('Sélectionner un logiciel')).toBeInTheDocument()
  })
}

describe('SynchronizationConnexions', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getProvidersByVenue').mockResolvedValue([
      {
        name: 'Ciné Office',
        id: 12,
        hasOffererProvider: false,
        isActive: true,
        enabledForPro: true,
      },
    ])
  })

  it('should render the section title', async () => {
    await renderSynchronizationConnexions()

    expect(screen.getByText('Gestion des synchronisations')).toBeInTheDocument()
  })

  it('should render the select software button', async () => {
    await renderSynchronizationConnexions()

    expect(screen.getByText('Sélectionner un logiciel')).toBeInTheDocument()
  })

  describe('when there are no venue providers', () => {
    it('should render the documentation banner', async () => {
      await renderSynchronizationConnexions([])

      expect(
        screen.getByText(/Vous pouvez donner les accès à vos logiciels tiers/)
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: /Accéder à la documentation/ })
      ).toBeInTheDocument()
    })
  })

  describe('when there are venue providers', () => {
    it('should render a card for each provider', async () => {
      await renderSynchronizationConnexions([defaultVenueProvider])

      expect(screen.getByTestId('venue-provider-card')).toBeInTheDocument()
      expect(screen.getByText('Ciné Office')).toBeInTheDocument()
    })

    it('should not render the documentation banner', async () => {
      await renderSynchronizationConnexions([defaultVenueProvider])

      expect(
        screen.queryByText(/Vous pouvez donner les accès à vos logiciels tiers/)
      ).not.toBeInTheDocument()
    })
  })
})
