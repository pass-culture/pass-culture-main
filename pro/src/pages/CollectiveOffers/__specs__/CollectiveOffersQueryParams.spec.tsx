import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer, SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOffers from '../CollectiveOffers'
import { collectiveOfferFactory } from '../utils/collectiveOffersFactories'

//FIX ME : extract inital values and constant to reduce code duplication with CollectiveOffers.spec.tsx

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: vi.fn(),
}))

const renderOffers = async (
  storeOverrides: Store,
  filters: Partial<SearchFiltersParams> & {
    page?: number
  } = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  renderWithProviders(
    <router.Routes>
      <router.Route path="/offres/collectives" element={<CollectiveOffers />} />

      <router.Route
        path="/offres"
        element={
          <>
            <h1>Offres individuelles</h1>
          </>
        }
      ></router.Route>
    </router.Routes>,
    {
      storeOverrides,
      initialRouterEntries: [route],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  return {
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
      proLabel: 'Evènement ciné',
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
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    isVirtual: false,
  },
  {
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  },
]

vi.mock('repository/venuesService', () => ({
  ...vi.importActual('repository/venuesService'),
}))

vi.mock('apiClient/api', () => ({
  api: {
    listOffers: vi.fn(),
    getCategories: vi.fn().mockResolvedValue(categoriesAndSubcategories),
    getCollectiveOffers: vi.fn(),
    getOfferer: vi.fn(),
    getVenues: vi.fn().mockResolvedValue({ venues: proVenues }),
  },
}))

vi.mock('utils/date', () => ({
  ...vi.importActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

vi.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: vi.fn().mockReturnValue(true),
}))

describe('route CollectiveOffers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
  }
  let store: any
  let offersRecap: Offer[]
  const mockNavigate = vi.fn()

  beforeEach(() => {
    currentUser = {
      id: 'EY',
      isAdmin: false,
      name: 'Current User',
    }
    store = {
      user: {
        initialized: true,
        currentUser,
      },
      offers: {
        searchFilters: DEFAULT_SEARCH_FILTERS,
      },
    }
    offersRecap = [collectiveOfferFactory()]
    jest
      .spyOn(api, 'getCollectiveOffers')
      // @ts-expect-error FIX ME
      .mockResolvedValue(offersRecap)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // Given
      const offersRecap = Array.from({ length: 11 }, () =>
        collectiveOfferFactory()
      )
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
      await renderOffers(store)
      const nextPageIcon = screen.getByRole('button', { name: 'Page suivante' })

      // When
      await userEvent.click(nextPageIcon)

      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives?page=2')
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      // Given
      await renderOffers(store)
      // When
      await userEvent.type(
        screen.getByPlaceholderText('Rechercher par nom d’offre'),
        'AnyWord'
      )
      await userEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?nom-ou-isbn=AnyWord'
      )
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      // Given
      await renderOffers(store)
      // When
      await userEvent.clear(
        screen.getByPlaceholderText('Rechercher par nom d’offre')
      )
      await userEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives')
    })

    it('should have venue value when user filters by venue', async () => {
      // Given
      await renderOffers(store)
      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')
      // When
      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(mockNavigate).toHaveBeenCalledWith(
        `/offres/collectives?lieu=${proVenues[0].id}`
      )
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
      vi.spyOn(api, 'getCategories').mockResolvedValue({
        categories: [
          { id: 'test_id_1', proLabel: 'My test value', isSelectable: true },
          {
            id: 'test_id_2',
            proLabel: 'My second test value',
            isSelectable: true,
          },
        ],
        subcategories: [
          // @ts-expect-error FIX ME
          {
            id: 'test_sub_id_1',
            categoryId: 'test_id_1',
            isSelectable: true,
            canBeEducational: true,
          },
          // @ts-expect-error FIX ME
          {
            id: 'test_sub_id_2',
            categoryId: 'test_id_2',
            canBeEducational: true,
            isSelectable: true,
          },
        ],
      })
      await renderOffers(store)
      const firstTypeOption = screen.getByRole('option', {
        name: 'My test value',
      })
      const typeSelect = screen.getByDisplayValue(ALL_CATEGORIES_OPTION.label)
      // When
      await userEvent.selectOptions(typeSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?categorie=test_id_1'
      )
    })

    it('should have status value when user filters by status', async () => {
      // Given
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        // @ts-expect-error FIX ME
        collectiveOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error collectiveOfferFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Réservée'))
      // When
      await userEvent.click(screen.getByText('Appliquer'))
      // Then
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offres/collectives?statut=reservee'
      )
    })

    it('should have status value be removed when user ask for all status', async () => {
      // Given
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        // @ts-expect-error FIX ME
        collectiveOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error collectiveOfferFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Toutes'))
      // When
      await userEvent.click(screen.getByText('Appliquer'))
      // Then
      expect(mockNavigate).toHaveBeenCalledWith('/offres/collectives')
    })

    it('should have offerer filter when user filters by offerer', async () => {
      // Given
      const filters = { offererId: 'A4' }
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })
      // When
      await renderOffers(store, filters)
      // Then
      const offererFilter = screen.getByText('La structure')
      expect(offererFilter).toBeInTheDocument()
    })

    it('should have offerer value be removed when user removes offerer filter', async () => {
      // Given
      const filters = { offererId: 'A4' }
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })
      await renderOffers(store, filters)
      // When
      await userEvent.click(screen.getByTestId('remove-offerer-filter'))
      // Then
      expect(screen.queryByText('La structure')).not.toBeInTheDocument()
    })
  })

  describe('page navigation', () => {
    it('should redirect to individual offers when user clicks on individual offers link', async () => {
      // Given

      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(
        // @ts-expect-error FIX ME
        offersRecap
      )
      await renderOffers(store)
      screen.getByText('Lancer la recherche')
      const individualAudienceLink = screen.getByText('Offres individuelles', {
        selector: 'span',
      })

      // When
      await userEvent.click(individualAudienceLink)

      // Then
      expect(screen.getByRole('heading', { name: 'Offres individuelles' }))
    })
  })
})
