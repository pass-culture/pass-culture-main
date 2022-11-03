import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import Notification from 'new_components/Notification/Notification'
import OfferLayout from 'pages/Offers/Offer/OfferLayout'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiCategories } from 'utils/fakeApi'

const mockLogEvent = jest.fn()

const GUYANA_CAYENNE_DEPT = '973'

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
    getVenue: jest.fn(),

    getStocks: jest.fn(),
    upsertStocks: jest.fn(),
    deleteStock: jest.fn(),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderOffers = (
  props,
  storeOverrides,
  pathname = '/offre/AG3A/individuel/creation/stocks'
) => {
  const store = configureTestStore(storeOverrides)
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: pathname }]}>
        <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
          {() => <OfferLayout {...props} />}
        </Route>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}

describe('stocks page', () => {
  let props
  let defaultOffer
  let stockId
  let store
  beforeEach(() => {
    store = {
      user: {
        currentUser: { publicName: 'François', isAdmin: false },
        initialized: true,
      },
    }
    props = {}

    defaultOffer = {
      id: 'AG3A',
      venue: {
        id: 'BC',
        departementCode: GUYANA_CAYENNE_DEPT,
        managingOfferer: {
          id: 'AB',
          name: 'offerer name',
        },
      },
      isEvent: false,
      status: 'DRAFT',
      stocks: [],
      dateCreated: '',
      fieldsUpdated: [],
      hasBookingLimitDatetimesPassed: true,
      isActive: true,
      isBookable: true,
      isDigital: true,
      isDuo: true,
      isEditable: true,
      isEducational: false,
      isNational: true,
      isThing: true,
      mediaUrls: [],
      mediations: [],
      name: 'offer name',
      nonHumanizedId: 1,
      product: {
        fieldsUpdated: [],
        id: 'product_id',
        isGcuCompatible: true,
        isNational: false,
        mediaUrls: [],
        name: 'product name',
        thumbCount: 0,
      },
      productId: 'product_id',
      subcategoryId: 'CONFERENCE',
      venueId: 'BC',
    }

    stockId = '2E'
    jest.spyOn(api, 'getOffer').mockResolvedValue(defaultOffer)
    api.getStocks.mockResolvedValue({ stocks: [] })
    api.getCategories.mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    api.deleteStock.mockResolvedValue({ id: stockId })
    loadFakeApiCategories()
    api.upsertStocks.mockResolvedValue({})
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 'AB',
          name: 'offerer name',
        },
      ],
    })
    jest.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        {
          id: 'BC',
          isVirtual: false,
          managingOffererId: 'AB',
          name: 'venue name',
          offererName: 'offerer name',
        },
      ],
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  describe('create', () => {
    describe('thing offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: false,
          isThing: true,
          isDigital: false,
          stocks: [],
        }
        jest.spyOn(api, 'getOffer').mockResolvedValue(noStockOffer)
      })

      it('should track when clicking on previous step button', async () => {
        // given
        renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Étape précédente'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'stocks',
            isDraft: true,
            isEdition: false,
            offerId: 'AG3A',
            to: 'details',
            used: 'StickyButtons',
          }
        )
      })

      it('should track stocks creation when clicking on validate button', async () => {
        // given
        api.upsertStocks.mockResolvedValue({})
        renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter un stock'))

        await userEvent.type(screen.getByLabelText('Prix'), '15')

        await userEvent.click(
          screen.getByLabelText('Date limite de réservation')
        )
        await userEvent.click(screen.getByText('22'))

        await userEvent.type(screen.getByLabelText('Quantité'), '15')

        // when
        await userEvent.click(screen.getByText('Étape suivante'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'stocks',
            isDraft: true,
            isEdition: false,
            offerId: 'AG3A',
            to: 'recapitulatif',
            used: 'StickyButtons',
          }
        )
      })

      it('should track stocks creation when clicking on save draft button', async () => {
        // given
        api.upsertStocks.mockResolvedValue({})
        store = {
          ...store,
          features: {
            list: [
              {
                isActive: true,
                name: 'OFFER_DRAFT_ENABLED',
                nameKey: 'OFFER_DRAFT_ENABLED',
              },
            ],
          },
        }
        renderOffers(props, store, '/offre/AG3A/individuel/creation/stocks')

        await userEvent.click(await screen.findByText('Ajouter un stock'))

        await userEvent.type(screen.getByLabelText('Prix'), '15')

        await userEvent.click(
          screen.getByLabelText('Date limite de réservation')
        )
        await userEvent.click(screen.getByText('22'))

        await userEvent.type(screen.getByLabelText('Quantité'), '15')

        // when
        await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

        // then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'stocks',
            isDraft: true,
            isEdition: false,
            offerId: 'AG3A',
            to: 'stocks',
            used: 'DraftButtons',
          }
        )
      })
    })

    describe('event offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }

        jest.spyOn(api, 'getOffer').mockResolvedValue(noStockOffer)
      })

      it('should track creation after submitting stock', async () => {
        // Given
        api.upsertStocks.mockResolvedValueOnce({})
        renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))

        await userEvent.type(screen.getByLabelText('Prix'), '10')

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_OFFER_FORM_NAVIGATION,
          {
            from: 'stocks',
            isDraft: true,
            isEdition: false,
            offerId: 'AG3A',
            to: 'recapitulatif',
            used: 'StickyButtons',
          }
        )
      })
    })
  })
})
