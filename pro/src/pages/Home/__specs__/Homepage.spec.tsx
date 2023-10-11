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
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  defaultGetOffererVenueResponseModel,
  defautGetOffererResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../Homepage'

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

describe('homepage', () => {
  const baseOfferers: GetOffererResponseModel[] = [
    {
      ...defautGetOffererResponseModel,
      id: 1,
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
      ...defautGetOffererResponseModel,
      id: 2,
      hasValidBankAccount: true,
    },
  ]

  const baseOfferersNames = baseOfferers.map(offerer => ({
    id: offerer.id,
    name: offerer.name,
  }))

  let store = {
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
    vi.spyOn(api, 'getVenueStats').mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
    vi.spyOn(api, 'postProFlags').mockResolvedValue()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  describe('it should render', () => {
    it('Pro flags should be sent on page load', async () => {
      renderHomePage(store)

      await waitFor(() => {
        expect(api.postProFlags).toHaveBeenCalledWith({
          firebase: { toto: 'tata' },
        })
      })
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

    describe('when clicking on anchor link to profile', () => {
      let scrollIntoViewMock: any

      beforeEach(async () => {
        scrollIntoViewMock = vi.fn()
        Element.prototype.scrollIntoView = scrollIntoViewMock
        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      })

      it('should smooth scroll to section if user doesnt prefer reduced motion', async () => {
        // when
        await userEvent.click(
          screen.getByRole('link', { name: 'Profil et aide' })
        )

        // then
        expect(scrollIntoViewMock).toHaveBeenCalledWith({
          behavior: 'smooth',
        })
      })
    })
    describe('when clicking on anchor link to offerers', () => {
      it('should trigger', async () => {
        renderHomePage(store)

        // when
        await userEvent.click(
          screen.getByRole('link', { name: 'Structures et lieux' })
        )

        // then
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_BREADCRUMBS_STRUCTURES
        )
      })
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

      it('should contains a link to access profile form', async () => {
        // when
        expect(screen.getAllByRole('link')[10]).toBeInTheDocument()
      })
    })

    describe('offererStats', () => {
      beforeEach(() => {
        store = {
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
          features: {
            list: [{ isActive: true, nameKey: 'ENABLE_OFFERER_STATS' }],
          },
        }
      })
      it('should display section when ff is active', async () => {
        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

        expect(
          screen.getByText('Statistiques', { selector: 'h2' })
        ).toBeInTheDocument()
      })

      describe('when clicking on anchor link to stats', () => {
        let scrollIntoViewMock: any

        beforeEach(async () => {
          scrollIntoViewMock = vi.fn()
          Element.prototype.scrollIntoView = scrollIntoViewMock
          renderHomePage(store)
          await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
        })

        it('should smooth scroll to section if user doesnt prefer reduced motion', async () => {
          // when
          const statLink = await screen.findByRole('link', {
            name: 'Statistiques',
          })
          await userEvent.click(statLink)

          // then
          expect(scrollIntoViewMock).toHaveBeenCalledWith({
            behavior: 'smooth',
          })
        })
      })
    })
  })
})
