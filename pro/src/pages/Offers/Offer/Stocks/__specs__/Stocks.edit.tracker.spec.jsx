import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route, Switch } from 'react-router'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import Notification from 'new_components/Notification/Notification'
import OfferLayout from 'pages/Offers/Offer/OfferLayout'
import { configureTestStore } from 'store/testUtils'
import { offerFactory, stockFactory } from 'utils/apiFactories'
import { loadFakeApiStocks } from 'utils/fakeApi'

const GUYANA_CAYENNE_DEPT = '973'
const mockLogEvent = jest.fn()

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
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
  pathname = '/offre/AG3A/individuel/stocks'
) => {
  const store = configureTestStore(storeOverrides)
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: pathname }]}>
        <Switch>
          <Route path="/offres">
            <div>Offres</div>
          </Route>
          <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
            {() => <OfferLayout {...props} />}
          </Route>
        </Switch>
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
      features: {
        initialized: true,
        list: [],
      },
    }
    props = {}

    defaultOffer = {
      ...offerFactory(),
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
      status: 'ACTIVE',
      stocks: [],
    }

    stockId = '2E'
    jest.spyOn(api, 'getOffer').mockResolvedValue(defaultOffer)
    api.getStocks.mockResolvedValue({ stocks: [] })
    api.getCategories.mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    api.deleteStock.mockResolvedValue({ id: stockId })
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

  describe('edit', () => {
    it('should track after validating stocks', async () => {
      // Given
      const stock = stockFactory()
      loadFakeApiStocks([stock])
      renderOffers(props, store)

      // When
      await userEvent.click(
        await screen.findByText('Enregistrer les modifications', {
          selector: 'button',
        })
      )

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isDraft: false,
          isEdition: true,
          offerId: 'AG3A',
          to: 'recapitulatif',
          used: 'StickyButtons',
        }
      )
    })

    it('should track after cancelling', async () => {
      // Given
      const stock = stockFactory()
      loadFakeApiStocks([stock])
      renderOffers(props, store)

      // When
      await userEvent.click(await screen.findByText('Annuler et quitter'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isDraft: false,
          isEdition: true,
          offerId: 'AG3A',
          to: 'Offers',
          used: 'StickyButtons',
        }
      )
    })
  })
})
