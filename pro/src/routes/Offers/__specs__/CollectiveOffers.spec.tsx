import '@testing-library/jest-dom'
import { parse } from 'querystring'

import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import type { Store } from 'redux'

import { api } from 'api/v1/api'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import {
  ALL_VENUES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Audience, Offer, TSearchFilters } from 'core/Offers/types'
import { configureTestStore } from 'store/testUtils'
import { offerFactory } from 'utils/apiFactories'

import Offers from '../Offers'

type TFilters = Partial<TSearchFilters> & {
  page?: number
  audience?: Audience
}

const renderOffers = (
  store: Store,
  filters: TFilters = DEFAULT_SEARCH_FILTERS
) => {
  const history = createMemoryHistory()
  const route = computeOffersUrl(filters)
  history.push(route)
  return {
    ...render(
      <Provider store={store}>
        <Router history={history}>
          <Offers />
        </Router>
      </Provider>
    ),
    history,
  }
}

const categoriesAndSubcategories = {
  categories: [
    { id: 'CINEMA', proLabel: 'Cinéma', isSelectable: true },
    { id: 'JEU', proLabel: 'Jeux', isSelectable: true },
    { id: 'TECHNIQUE', proLabel: 'Technique', isSelectable: false },
  ],
  subcategories: [
    {
      id: 'EVENEMENT_CINE',
      proLabel: 'Evénement ciné',
      canBeEducational: true,
      categoryId: 'CINEMA',
      isSelectable: true,
    },
    {
      id: 'CONCOURS',
      proLabel: 'Concours jeux',
      canBeEducational: false,
      categoryId: 'JEU',
      isSelectable: true,
    },
  ],
}

const proVenues = [
  {
    id: 'JI',
    name: 'Ma venue',
    offererName: 'Mon offerer',
    isVirtual: false,
  },
  {
    id: 'JQ',
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  },
]

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
  fetchAllVenuesByProUser: jest.fn().mockResolvedValue(proVenues),
}))

jest.mock('api/v1/api', () => ({
  api: {
    getOffersListOffers: jest.fn(),
    getCollectiveListCollectiveOffers: jest.fn(),
    getOfferersGetOfferer: jest.fn(),
    getOffersGetCategories: jest
      .fn()
      .mockResolvedValue(categoriesAndSubcategories),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('components/hooks/useActiveFeature', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(true),
}))

describe('route Offers - Collective tab', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
    publicName: string
  }
  let store: Store
  let offersRecap: Offer[]
  let filters: TFilters

  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      name: 'Current User',
      publicName: 'USER',
    }
    store = configureTestStore({
      data: {
        users: [currentUser],
      },
      user: {
        initialized: true,
      },
      offers: {
        searchFilters: DEFAULT_SEARCH_FILTERS,
      },
    })
    offersRecap = [offerFactory({ venue: proVenues[0] })]
    ;(api.getOffersListOffers as jest.Mock).mockResolvedValue(offersRecap)
    filters = {
      audience: Audience.COLLECTIVE,
    }
  })

  describe('render', () => {
    describe('filters', () => {
      it('should display only selectable categories eligible for EAC on filters', async () => {
        // When
        renderOffers(store, filters)
        await screen.findByText('Lancer la recherche')

        // Then
        await expect(
          screen.findByRole('option', { name: 'Cinéma' })
        ).resolves.toBeInTheDocument()
        await expect(
          screen.findByRole('option', { name: 'Jeux' })
        ).rejects.toBeTruthy()
        await expect(
          screen.findByRole('option', { name: 'Technique' })
        ).rejects.toBeTruthy()
      })
    })
  })

  describe('url query params', () => {
    it('should call collective adapter when audience query param value is collective', async () => {
      // Given
      ;(api.getCollectiveListCollectiveOffers as jest.Mock).mockResolvedValue(
        offersRecap
      )
      renderOffers(store, filters)
      await screen.findByText('Lancer la recherche')

      // Then
      expect(api.getCollectiveListCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })
  })

  describe('should reset filters', () => {
    it('should not remove audience query param if value is collective when clicking on "Réinitialiser les filtres"', async () => {
      ;(api.getOffersListOffers as jest.Mock)
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      const { history } = renderOffers(store, filters)

      const venueOptionToSelect = await screen.findByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName
      )

      userEvent.selectOptions(venueSelect, venueOptionToSelect)

      fireEvent.click(screen.getByText('Lancer la recherche'))

      fireEvent.click(screen.getByText('Réinitialiser les filtres'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        audience: 'collective',
      })
    })
  })
})
