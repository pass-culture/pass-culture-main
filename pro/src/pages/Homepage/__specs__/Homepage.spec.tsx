import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import type {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Homepage } from '../Homepage'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'GE' }),
}))

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn().mockReturnValue(false),
}))

const reloadFn = vi.fn()
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: {
    reload: reloadFn,
    href: '',
  },
  writable: true,
})

const baseOfferers: GetOffererResponseModel[] = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: 'Structure 1',
    isActive: true,
    hasDigitalVenueAtLeastOneOffer: true,
    isValidated: true,
    managedVenues: [
      {
        ...defaultGetOffererVenueResponseModel,
        id: 1,
        isVirtual: true,
      },
      {
        ...defaultGetOffererVenueResponseModel,
        id: 2,
        isVirtual: false,
      },
      {
        ...defaultGetOffererVenueResponseModel,
        id: 3,
        isVirtual: false,
      },
    ],
    hasValidBankAccount: false,
  },
  {
    ...defaultGetOffererResponseModel,
    id: 2,
    name: 'Structure 2',
    hasValidBankAccount: true,
  },
  {
    ...defaultGetOffererResponseModel,
    id: 3,
    name: 'Structure 3',
    canDisplayHighlights: false,
  },
]

const renderHomePage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<Homepage />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { currentOfferer: baseOfferers[0] },
    },
    ...options,
  })
}

const mockLogEvent = vi.fn()

describe('Homepage', () => {
  const baseOfferersNames = baseOfferers.map(
    (offerer): GetOffererNameResponseModel => ({
      id: offerer.id,
      name: offerer.name,
      allowedOnAdage: true,
    })
  )

  beforeEach(() => {
    vi.spyOn(api, 'getProfile')
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getOffererStats').mockResolvedValueOnce({
      jsonData: {
        dailyViews: [],
        topOffers: [],
        totalViewsLast30Days: 0,
      },
      syncDate: null,
      offererId: 1,
    })
    vi.spyOn(api, 'getHighlights').mockResolvedValue([])
  })

  it('the user should see the home offer steps if they do not have any venues', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[1])

    renderHomePage({
      storeOverrides: {
        offerer: {
          currentOfferer: baseOfferers[1],
        },
      },
    })

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(await screen.findByTestId('home-offer-steps')).toBeInTheDocument()
  })

  it('the user should not see the home offer steps if they have some venues', async () => {
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  describe('render statistics dashboard', () => {
    it('should display statistics dashboard when selected offerer is active and validated', async () => {
      renderHomePage()

      expect(
        await screen.findByText('Présence sur l’application pass Culture')
      ).toBeInTheDocument()
    })

    it('should not display statistics dashboard when selected offerer is active but not validated', async () => {
      renderHomePage({
        storeOverrides: {
          offerer: {
            currentOfferer: {
              ...defaultGetOffererResponseModel,
              id: 3,
              name: 'Structure 3',
              hasValidBankAccount: true,
              isValidated: false,
              isActive: true,
            },
          },
        },
      })

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur l’application pass Culture')
      ).not.toBeInTheDocument()
    })

    it('should not display statistics dashboard when selected offerer is validated but not active', async () => {
      renderHomePage({
        storeOverrides: {
          offerer: {
            currentOfferer: {
              ...defaultGetOffererResponseModel,
              id: 3,
              name: 'Structure 3',
              hasValidBankAccount: true,
              isValidated: true,
              isActive: false,
            },
          },
        },
      })

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur l’application pass Culture')
      ).not.toBeInTheDocument()
    })
  })
  describe('render highlights', () => {
    it('should display highlights when selected offerer can display highlights', async () => {
      renderHomePage({ features: ['WIP_HIGHLIGHT'] })

      expect(
        await screen.findByText('Parcourir les temps forts')
      ).toBeInTheDocument()
    })

    it('should not display highlights when the WIP_HIGHLIGHT feature is not active', async () => {
      renderHomePage()

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Parcourir les temps forts')
      ).not.toBeInTheDocument()
    })

    it('should not display highlights when selected offerer cannot display highlights', async () => {
      renderHomePage({
        features: ['WIP_HIGHLIGHT'],
        storeOverrides: {
          offerer: {
            currentOfferer: baseOfferers[2],
          },
        },
      })

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Parcourir les temps forts')
      ).not.toBeInTheDocument()
    })
  })
})
