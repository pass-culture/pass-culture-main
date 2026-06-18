import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as SynchronizationProviders } from './SynchronizationProviders'

vi.mock(
  './components/VenueProvidersManager/SynchronizationConnexions/SynchronizationConnexions',
  () => ({
    SynchronizationConnexions: ({
      venueProviders,
    }: {
      venueProviders: unknown[]
    }) => (
      <div data-testid="synchronization-connexions">
        {venueProviders.length} fournisseur(s)
      </div>
    ),
  })
)

vi.mock('@/apiClient/api', () => ({
  api: {
    listVenueProviders: vi.fn(),
  },
}))

const renderSynchronizationProviders = (
  venueOverrides: Partial<GetVenueResponseModel> = {},
  options?: RenderWithProvidersOptions
) => {
  const user = sharedCurrentUserFactory()
  const venue = { ...defaultGetVenue, ...venueOverrides }

  return renderWithProviders(<SynchronizationProviders />, {
    user,
    ...options,
    storeOverrides: {
      user: { currentUser: user, selectedPartnerVenue: venue },
      ...options?.storeOverrides,
    },
  })
}

describe('SynchronizationProviders', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listVenueProviders').mockResolvedValue({
      venueProviders: [],
    })
  })

  it('should call listVenueProviders with the venue id', async () => {
    renderSynchronizationProviders({ id: 1 })

    await waitFor(() => {
      expect(api.listVenueProviders).toHaveBeenCalledWith({
        path: { venue_id: 1 },
      })
    })
  })

  describe('when the venue is not virtual', () => {
    it('should render SynchronizationConnexions with no providers', async () => {
      renderSynchronizationProviders()

      expect(
        await screen.findByTestId('synchronization-connexions')
      ).toBeInTheDocument()
      expect(screen.getByText('0 fournisseur(s)')).toBeInTheDocument()
    })

    it('should render SynchronizationConnexions with loaded providers', async () => {
      vi.spyOn(api, 'listVenueProviders').mockResolvedValue({
        venueProviders: [defaultVenueProvider],
      })

      renderSynchronizationProviders()

      expect(await screen.findByText('1 fournisseur(s)')).toBeInTheDocument()
    })
  })
})
