import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { RemoteContextProvider } from 'context/remoteConfigContext'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { renderWithProviders } from 'utils/renderWithProviders'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import Homepage from '../Homepage'

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    listOfferersNames: jest.fn(),
    getOfferer: jest.fn(),
    getVenueStats: jest.fn(),
  },
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn(),
}))

jest.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asString: () => 'GE' }),
}))

jest.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({ remoteConfig: {} }),
}))

jest.mock('hooks/useNewOfferCreationJourney', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false),
}))

const renderHomePage = storeOverrides => {
  renderWithProviders(
    <RemoteContextProvider>
      <Homepage />
    </RemoteContextProvider>,
    { storeOverrides }
  )
}

const mockLogEvent = jest.fn()

describe('homepage', () => {
  let baseOfferers
  let baseOfferersNames
  let store

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
    }
    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        id: 'GE',
        nonHumanizedId: 6,
        isValidated: true,
        lastProviderId: null,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '111111111',
        managedVenues: [
          {
            id: 'test_venue_id_1',
            isVirtual: true,
            managingOffererId: 'GE',
            name: 'Le Sous-sol (Offre numérique)',
            offererName: 'Bar des amis',
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_2',
            isVirtual: false,
            managingOffererId: 'GE',
            name: 'Le Sous-sol (Offre physique)',
            offererName: 'Bar des amis',
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_3',
            isVirtual: false,
            managingOffererId: 'GE',
            name: 'Le deuxième Sous-sol (Offre physique)',
            offererName: 'Bar des amis',
            publicName: 'Le deuxième Sous-sol',
            nOffers: 2,
          },
        ],
      },
      {
        address: 'RUE DE NIEUPORT',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        id: 'FQ',
        nonHumanizedId: 12,
        isValidated: true,
        lastProviderId: null,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [],
      },
    ]

    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
      nonHumanizedId: offerer.nonHumanizedId,
    }))
    api.getOfferer.mockResolvedValue(baseOfferers[0])
    api.listOfferersNames.mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    api.getVenueStats.mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  describe('it should render', () => {
    describe('new venue offer journey', () => {
      beforeEach(() => {
        jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
      })

      it('the user should see the home offer steps if they do not have any venues', async () => {
        api.getOfferer.mockResolvedValue(baseOfferers[1])
        api.listOfferersNames.mockResolvedValue({
          offerersNames: [baseOfferersNames[1]],
        })

        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

        expect(screen.getByTestId('home-offer-steps')).toBeInTheDocument()
      })

      it('the user should not see the home offer steps if they have some venues', async () => {
        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

        expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
      })
    })

    describe('when clicking on anchor link to profile', () => {
      let scrollIntoViewMock
      beforeEach(async () => {
        scrollIntoViewMock = jest.fn()
        Element.prototype.scrollIntoView = scrollIntoViewMock
        renderHomePage(store)
        await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
      })

      it('should smooth scroll to section if user doesnt prefer reduced motion', async () => {
        // given
        doesUserPreferReducedMotion.mockReturnValue(false)

        // when
        await userEvent.click(
          screen.getByRole('link', { name: 'Profil et aide' })
        )

        // then
        expect(scrollIntoViewMock).toHaveBeenCalledWith({
          behavior: 'smooth',
        })
      })

      it('should jump to section if user prefers reduced motion', async () => {
        // given
        doesUserPreferReducedMotion.mockReturnValue(true)

        // when
        await userEvent.click(
          screen.getByRole('link', { name: 'Profil et aide' })
        )

        // then
        expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'auto' })
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_BREADCRUMBS_PROFILE_AND_HELP
        )
      })
    })
    describe('when clicking on anchor link to offerers', () => {
      it('should trigger', async () => {
        renderHomePage(store)
        // given
        doesUserPreferReducedMotion.mockReturnValue(true)

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
        let scrollIntoViewMock
        beforeEach(async () => {
          scrollIntoViewMock = jest.fn()
          Element.prototype.scrollIntoView = scrollIntoViewMock
          renderHomePage(store)
          await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
        })

        it('should smooth scroll to section if user doesnt prefer reduced motion', async () => {
          // given
          doesUserPreferReducedMotion.mockReturnValue(false)

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
