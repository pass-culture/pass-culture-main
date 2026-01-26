import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Homepage } from './Homepage'

const renderHomePage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<Homepage />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: defaultGetOffererVenueResponseModel,
      },
      offerer: {
        currentOfferer: {
          ...defaultGetOffererResponseModel,
          managedVenues: [defaultGetOffererVenueResponseModel],
        },
      },
    },
    ...options,
  })
}

vi.mock('./components/Offerers/Offerers', () => ({
  Offerers: () => <div data-testid="mock-offerers" />,
}))

describe('Homepage', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
  })

  describe('with WIP_ENABLE_NEW_PRO_HOME feature flag', () => {
    it('should render old homepage when WIP_SWITCH_VENUE is off', async () => {
      renderHomePage({ features: ['WIP_ENABLE_NEW_PRO_HOME'] })
      expect(
        await screen.findByRole('heading', { level: 1 })
      ).toHaveTextContent('Bienvenue sur votre espace partenaire')
    })

    it('should render new homepage when WIP_SWITCH_VENUE is on', async () => {
      renderHomePage({
        features: ['WIP_ENABLE_NEW_PRO_HOME', 'WIP_SWITCH_VENUE'],
      })
      expect(
        await screen.findByRole('heading', { level: 1 })
      ).toHaveTextContent('Votre espace Nom public de la structure')
    })
  })
  describe('without WIP_ENABLE_NEW_PRO_HOME feature flag', () => {
    it('should render old homepage', async () => {
      renderHomePage({ features: ['WIP_SWITCH_VENUE'] })
      expect(
        await screen.findByRole('heading', { level: 1 })
      ).toHaveTextContent('Bienvenue sur votre espace partenaire')
    })
  })
})
