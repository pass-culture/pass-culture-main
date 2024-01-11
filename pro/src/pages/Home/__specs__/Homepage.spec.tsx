import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { RemoteContextProvider } from 'context/remoteConfigContext'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Homepage, SAVED_OFFERER_ID_KEY } from '../Homepage'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'GE' }),
}))

vi.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({ remoteConfig: {}, remoteConfigData: { toto: 'tata' } }),
}))

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn().mockReturnValue(false),
}))
vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

const renderHomePage = (storeOverrides: any) => {
  renderWithProviders(
    <RemoteContextProvider>
      <Homepage />
    </RemoteContextProvider>,
    { storeOverrides }
  )
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

  const baseOfferersNames = baseOfferers.map((offerer) => ({
    id: offerer.id,
    name: offerer.name,
  }))

  const store = {
    user: {
      currentUser: {
        id: 'fake_id',
        firstName: 'John',
        lastName: 'Do',
        email: 'john.do@dummy.xyz',
        phoneNumber: '01 00 00 00 00',
        hasSeenProTutorials: true,
      },
      initialized: true,
    },
    features: {},
  }

  beforeEach(() => {
    vi.spyOn(api, 'getProfile')
    vi.spyOn(router, 'useLoaderData').mockReturnValue({
      venueTypes: [],
      offererNames: baseOfferersNames,
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[0])
    vi.spyOn(api, 'postProFlags').mockResolvedValue()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
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

  it('pro flags should be sent on page load', async () => {
    renderHomePage(store)

    await waitFor(() => {
      expect(api.postProFlags).toHaveBeenCalledWith({
        firebase: { toto: 'tata' },
      })
    })
    expect(api.postProFlags).toHaveBeenCalledTimes(1)
  })

  it('the user should see the home offer steps if they do not have any venues', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[1])

    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByTestId('home-offer-steps')).toBeInTheDocument()
  })

  it('the user should not see the home offer steps if they have some venues', async () => {
    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should display profile and support section and subsection titles', async () => {
    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByText('Profil et aide', { selector: 'h2' })
    ).toBeInTheDocument()
    expect(screen.getByText('Profil')).toBeInTheDocument()
    expect(screen.getByText('Aide et support')).toBeInTheDocument()
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

      renderHomePage(store)

      expect(
        await screen.findByText('Présence sur le pass Culture')
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
      renderHomePage(store)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur le pass Culture')
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
      renderHomePage(store)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur le pass Culture')
      ).not.toBeInTheDocument()
    })
  })

  it('should display new offerer venues informations when selected offerer change', async () => {
    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()

    const newOfferer = {
      ...defaultGetOffererResponseModel,
      isActive: true,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          id: 1,
          isVirtual: false,
          name: 'Autre lieu',
          publicName: null,
        },
      ],
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(newOfferer)

    await userEvent.selectOptions(
      screen.getByLabelText('Structure'),
      'Structure 2'
    )

    expect(await screen.findByText('Autre lieu')).toBeInTheDocument()

    expect(screen.getByText('Gérer ma page')).toBeInTheDocument()
  })

  it('should load saved offerer in localStorage if no get parameter', async () => {
    const offererId = baseOfferers[1].id
    localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId.toString())

    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOfferer).toHaveBeenCalledWith(offererId)
  })

  it('should not used saved offerer in localStorage if it is not an option', async () => {
    localStorage.setItem(SAVED_OFFERER_ID_KEY, '123456')

    renderHomePage(store)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOfferer).toHaveBeenCalledWith(baseOfferers[0].id)
  })
})
