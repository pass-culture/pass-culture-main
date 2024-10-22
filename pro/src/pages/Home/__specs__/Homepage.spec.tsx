import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'apiClient/helpers'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'

import { Homepage } from '../Homepage'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'GE' }),
}))

vi.mock('commons/utils/windowMatchMedia', () => ({
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

const renderHomePage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<Homepage />, {
    user,
    storeOverrides: {
      user: {
        selectedOffererId: 1,
        currentUser: user,
      },
    },
    ...options,
  })
}

const mockLogEvent = vi.fn()

describe('Homepage', () => {
  const baseOfferers: GetOffererResponseModel[] = [
    {
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Structure 1',
      isActive: true,
      hasDigitalVenueAtLeastOneOffer: true,
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
  ]

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
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[0])
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
  })

  it('the user should see the home offer steps if they do not have any venues', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[1])

    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(await screen.findByTestId('home-offer-steps')).toBeInTheDocument()
  })

  it('the user should see the home even when not validated', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      status: HTTP_STATUS.FORBIDDEN,
    })

    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.listOfferersNames).toHaveBeenCalled()
    expect(
      screen.getByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })

  it('the user should not see the home offer steps if they have some venues', async () => {
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should send user-pro-flag data', async () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      DATA: 'TEST',
    })
    vi.spyOn(api, 'postProFlags').mockResolvedValue()
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await waitFor(() => {
      expect(api.postProFlags).toHaveBeenCalledWith({
        firebase: { DATA: 'TEST' },
      })
    })
  })

  describe('render statistics dashboard', () => {
    it('should display statistics dashboard when selected offerer is active and validated', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 3,
        name: 'Structure 3',
        hasValidBankAccount: true,
        isValidated: true,
        isActive: true,
      })

      renderHomePage()

      expect(
        await screen.findByText('Présence sur l’application pass Culture')
      ).toBeInTheDocument()
    })

    it('should not display statistics dashboard when selected offerer is active but not validated', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 3,
        name: 'Structure 3',
        hasValidBankAccount: true,
        isValidated: false,
        isActive: true,
      })
      renderHomePage()
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur l’application pass Culture')
      ).not.toBeInTheDocument()
    })

    it('should not display statistics dashboard when selected offerer is validated but not active', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 3,
        name: 'Structure 3',
        hasValidBankAccount: true,
        isValidated: true,
        isActive: false,
      })
      renderHomePage()
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur l’application pass Culture')
      ).not.toBeInTheDocument()
    })
  })

  it('should display pending offerer banner when rattachement is pending', async () => {
    // TODO: getOfferer called twice
    vi.spyOn(api, 'getOfferer').mockRejectedValue({ status: 403 })

    renderHomePage()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })
})
