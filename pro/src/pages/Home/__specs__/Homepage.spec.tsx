import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { RemoteContextProvider } from 'context/remoteConfigContext'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Homepage } from '../Homepage'

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
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: baseOfferersNames,
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

  describe('it should render', () => {
    it('Pro flags should be sent on page load', async () => {
      renderHomePage(store)

      await waitFor(() => {
        expect(api.postProFlags).toHaveBeenCalledWith({
          firebase: { toto: 'tata' },
        })
      })
      expect(api.postProFlags).toHaveBeenCalledTimes(1)
    })

    it('the user should see the home offer steps if they do not have any venues', async () => {
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [baseOfferersNames[1]],
      })
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

    describe('profileAndSupport', () => {
      beforeEach(async () => {
        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      })

      it('should display section and subsection titles', () => {
        expect(
          screen.getByText('Profil et aide', { selector: 'h2' })
        ).toBeInTheDocument()
        expect(screen.getByText('Profil')).toBeInTheDocument()
        expect(screen.getByText('Aide et support')).toBeInTheDocument()
      })

      it('should contains a link to access profile form', () => {
        // when
        expect(screen.getAllByRole('link')[10]).toBeInTheDocument()
      })
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
      screen.getByLabelText('Sélectionner une structure'),
      'Structure 2'
    )

    expect(await screen.findByText('Autre lieu')).toBeInTheDocument()

    expect(screen.getByText('Gérer ma page')).toBeInTheDocument()
  })
})
