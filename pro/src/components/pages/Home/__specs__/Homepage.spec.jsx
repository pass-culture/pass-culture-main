import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import Homepage from '../Homepage'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/offerer/demarchesSimplifiees/procedure',
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getBusinessUnits: jest.fn(),
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
  setHasSeenRGSBanner: jest.fn(),
  updateUserInformations: jest.fn().mockResolvedValue({}),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
  },
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn(),
}))

const renderHomePage = store => {
  render(
    <Provider store={store}>
      <MemoryRouter>
        <Homepage />
      </MemoryRouter>
    </Provider>
  )
}

const mockLogEvent = jest.fn()

describe('homepage', () => {
  let baseOfferers
  let baseOfferersNames
  let store

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: {
          id: 'fake_id',
          firstName: 'John',
          lastName: 'Do',
          email: 'john.do@dummy.xyz',
          phoneNumber: '01 00 00 00 00',
        },
        initialized: true,
      },
    })
    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        bic: 'test bic 01',
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
        iban: 'test iban 01',
        id: 'GE',
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
        bic: 'test bic 02',
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
        iban: 'test iban 02',
        id: 'FQ',
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
    }))
    pcapi.getBusinessUnits.mockResolvedValue([])
    pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
    pcapi.getAllOfferersNames.mockResolvedValue(baseOfferersNames)
    pcapi.getVenueStats.mockResolvedValue({
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
    describe('when clicking on anchor link to profile', () => {
      let scrollIntoViewMock
      beforeEach(async () => {
        scrollIntoViewMock = jest.fn()
        Element.prototype.scrollIntoView = scrollIntoViewMock
        await renderHomePage(store)
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
        await renderHomePage(store)
        // given
        doesUserPreferReducedMotion.mockReturnValue(true)

        // when
        await userEvent.click(screen.getByRole('link', { name: 'Structures' }))

        // then
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_BREADCRUMBS_STRUCTURES
        )
      })
    })

    describe('rGS Banner', () => {
      it('should close and register when user clicks close button', async () => {
        const spyRegister = jest
          .spyOn(pcapi, 'setHasSeenRGSBanner')
          .mockResolvedValue()
        renderHomePage(store)
        await userEvent.click(
          screen.getByRole('button', { name: /Masquer le bandeau/ })
        )
        expect(spyRegister).toHaveBeenCalledTimes(1)
        expect(screen.queryByText(/Soyez vigilant/)).not.toBeInTheDocument()
      })
      it('should not display if user has already seen', () => {
        jest.spyOn(api, 'getProfile').mockResolvedValue({ hasSeenProRgs: true })
        store = configureTestStore({
          user: {
            currentUser: {
              hasSeenProRgs: true,
            },
          },
        })
        renderHomePage(store)
        expect(screen.queryByText(/Soyez vigilant/)).not.toBeInTheDocument()
      })
    })

    describe('profileAndSupport', () => {
      beforeEach(async () => {
        renderHomePage(store)
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
        store = configureTestStore({
          user: {
            currentUser: {
              id: 'fake_id',
              firstName: 'John',
              lastName: 'Do',
              email: 'john.do@dummy.xyz',
              phoneNumber: '01 00 00 00 00',
            },
            initialized: true,
          },
          features: {
            list: [{ isActive: true, nameKey: 'ENABLE_OFFERER_STATS' }],
          },
        })
      })
      it('should display section when ff is active', async () => {
        await renderHomePage(store)
        expect(
          screen.getByText('Statistiques', { selector: 'h2' })
        ).toBeInTheDocument()
      })
    })
  })
})
