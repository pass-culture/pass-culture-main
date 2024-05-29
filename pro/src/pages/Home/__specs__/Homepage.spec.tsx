import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Homepage } from '../Homepage'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'GE' }),
}))

vi.mock('utils/windowMatchMedia', () => ({
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
  renderWithProviders(<Homepage />, {
    user: sharedCurrentUserFactory(),
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

  it('the user should not see the home offer steps if they have some venues', async () => {
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should display profile and support section and subsection titles', async () => {
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      await screen.findByText('Profil et aide', { selector: 'h2' })
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

      renderHomePage()

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
      renderHomePage()
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
      renderHomePage()
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText('Présence sur le pass Culture')
      ).not.toBeInTheDocument()
    })
  })

  it('should display new offerer venues informations when selected offerer change', async () => {
    renderHomePage()
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

    expect(
      screen.getByText('Gérer votre page pour le grand public')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour les enseignants')
    ).toBeInTheDocument()
  })

  it('should load saved offerer in localStorage if no get parameter', async () => {
    const offererId = baseOfferers[1].id
    localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId.toString())

    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOfferer).toHaveBeenCalledWith(offererId)
  })

  it('should not used saved offerer in localStorage if it is not an option', async () => {
    localStorage.setItem(SAVED_OFFERER_ID_KEY, '123456')

    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOfferer).toHaveBeenCalledWith(baseOfferers[0].id)
  })

  it('should display pending offerer banner when rattachement is pending', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({ status: 403 })

    renderHomePage()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })

  describe('beta banner', () => {
    it('should not display the banner if the user is eligible but is already a beta tester', async () => {
      renderHomePage({
        features: ['WIP_ENABLE_PRO_SIDE_NAV'],
        user: sharedCurrentUserFactory({
          navState: {
            eligibilityDate: '2020-04-03T12:00:00+04:00',
            newNavDate: '2020-04-03T12:00:00+04:00',
          },
        }),
      })
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      expect(
        screen.queryByText(/Une nouvelle interface sera bientôt disponible/)
      ).not.toBeInTheDocument()
    })

    it('should not display the banner if the user has an eligiblity date in the future', async () => {
      const now = new Date()
      const later = now.setDate(now.getDate() + 14)
      renderHomePage({
        features: ['WIP_ENABLE_PRO_SIDE_NAV'],
        user: sharedCurrentUserFactory({
          navState: {
            eligibilityDate: formatBrowserTimezonedDateAsUTC(later),
          },
        }),
      })
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      expect(
        screen.queryByText(/Une nouvelle interface sera bientôt disponible/)
      ).not.toBeInTheDocument()
    })

    it('should display the banner if the user is eligible', async () => {
      vi.spyOn(api, 'postNewProNav').mockResolvedValue()

      renderHomePage({
        features: ['WIP_ENABLE_PRO_SIDE_NAV'],
        user: sharedCurrentUserFactory({
          navState: {
            eligibilityDate: '2020-04-03T12:00:00+04:00',
          },
          hasSeenProTutorials: true,
        }),
      })

      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      expect(
        screen.getByText(/Une nouvelle interface sera bientôt disponible/)
      ).toBeInTheDocument()

      await userEvent.click(screen.getByText(/Activer dès maintenant/))
      expect(api.postNewProNav).toHaveBeenCalledTimes(1)
      expect(
        await screen.findByText(/Bienvenue sur la nouvelle interface/)
      ).toBeInTheDocument()
    })

    it('should not display the banner if the user already closed the banner', async () => {
      localStorage.setItem('HAS_CLOSED_BETA_TEST_BANNER', 'true')
      renderHomePage({
        features: ['WIP_ENABLE_PRO_SIDE_NAV'],
        user: sharedCurrentUserFactory({
          navState: {
            eligibilityDate: '2020-04-03T12:00:00+04:00',
          },
        }),
      })
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      expect(
        screen.queryByText(/Une nouvelle interface sera bientôt disponible/)
      ).not.toBeInTheDocument()
    })
  })
})
