import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { Notification } from 'new_components/Notification'
import { configureTestStore } from 'store/testUtils'

import OfferLayout from '../../OfferLayout'

import { getOfferInputForField } from './helpers'

const mockLogEvent = jest.fn()

jest.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    patchOffer: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
    getVenue: jest.fn(),
    getCategories: jest.fn(),
    getStocks: jest.fn(),
  },
}))

const renderOffers = async (props, store, queryParams = '') => {
  const rtlReturns = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/offre/ABC12/individuel/brouillon',
            search: queryParams,
          },
        ]}
      >
        <Route path={['/offre/:offerId([A-Z0-9]+)/individuel']}>
          <>
            <OfferLayout {...props} />
            <Notification />
          </>
        </Route>
      </MemoryRouter>
    </Provider>
  )
  await getOfferInputForField('categoryId')
  return rtlReturns
}

describe('offerDetails - Draft', () => {
  let editedOffer
  let venueManagingOfferer
  let props
  let store
  let editedOfferVenue
  let categories

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: {
          publicName: 'François',
          isAdmin: false,
          email: 'francois@example.com',
        },
        initialized: true,
      },
      features: {
        list: [
          {
            isActive: true,
            nameKey: 'OFFER_DRAFT_ENABLED',
          },
        ],
      },
    })

    venueManagingOfferer = {
      id: 'BA',
      name: 'La structure',
    }

    editedOfferVenue = {
      id: 'AB',
      isVirtual: false,
      managingOfferer: venueManagingOfferer,
      managingOffererId: venueManagingOfferer.id,
      name: 'Le lieu',
      offererName: 'La structure',
      bookingEmail: 'venue@example.com',
      withdrawalDetails: null,
      audioDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      motorDisabilityCompliant: null,
      visualDisabilityCompliant: null,
    }
    editedOffer = {
      id: 'ABC12',
      nonHumanizedId: 111,
      subcategoryId: 'ID',
      name: 'My edited offer',
      venue: editedOfferVenue,
      venueId: editedOfferVenue.id,
      thumbUrl: null,
      description: 'My edited description',
      withdrawalDetails: 'My edited withdrawal details',
      status: 'DRAFT',
      extraData: {
        musicType: '501',
        musicSubType: '502',
        isbn: '1234567890123',
      },
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
      stocks: [],
    }
    categories = {
      categories: [
        {
          id: 'ID',
          name: 'Musique',
          proLabel: 'Musique',
          appLabel: 'Musique',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'ID',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: true,
          canBeEducational: true,
          isSelectable: true,
        },
        {
          id: 'ID2',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: false,
          canBeEducational: true,
          isSelectable: true,
        },
      ],
    }
    props = {
      setShowThumbnailForm: jest.fn(),
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(editedOffer)
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [venueManagingOfferer] })
    jest
      .spyOn(api, 'getVenues')
      .mockResolvedValue({ venues: [editedOfferVenue] })

    api.getCategories.mockResolvedValue(categories)
    api.getVenue.mockReturnValue(Promise.resolve())
    api.getStocks.mockReturnValue(Promise.resolve({ stocks: [] }))
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  describe('render when completing a draft offer', () => {
    it('should display the right title and redirect to brouillon stock page', async () => {
      await renderOffers(props, store)

      expect(screen.getByText("Compléter l'offre")).toBeInTheDocument()

      await userEvent.click(screen.getByText('Étape suivante'))

      expect(
        await screen.findByRole('heading', { name: 'Stocks et prix', level: 3 })
      ).toBeInTheDocument()
      expect(screen.getByText("Compléter l'offre")).toBeInTheDocument()
    })

    it('should track information when clicking on "Étape suivante"', async () => {
      await renderOffers(props, store)

      await userEvent.click(screen.getByText('Étape suivante'))

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'details',
          isDraft: true,
          isEdition: true,
          offerId: 'ABC12',
          to: 'stocks',
          used: 'StickyButtons',
        }
      )
    })

    it('should track information when clicking on "Enregistrer le brouillon"', async () => {
      await renderOffers(props, store)

      await userEvent.click(
        screen.getByRole('button', { name: 'Sauvegarder le brouillon' })
      )

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'details',
          isDraft: true,
          isEdition: true,
          offerId: 'ABC12',
          to: 'details',
          used: 'DraftButtons',
        }
      )
    })
  })
})
