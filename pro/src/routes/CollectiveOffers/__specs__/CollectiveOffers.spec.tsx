import '@testing-library/jest-dom'

import {
  ALL_CATEGORIES_OPTION,
  ALL_OFFERS,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer, TSearchFilters } from 'core/Offers/types'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import CollectiveOffers from '../CollectiveOffers'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router'
import type { Store } from 'redux'
import { api } from 'apiClient/api'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { configureTestStore } from 'store/testUtils'
import { createMemoryHistory } from 'history'
import { offerFactory } from 'utils/apiFactories'
import { parse } from 'querystring'
import userEvent from '@testing-library/user-event'

const renderOffers = (
  store: Store,
  filters: Partial<TSearchFilters> & {
    page?: number
  } = DEFAULT_SEARCH_FILTERS
) => {
  const history = createMemoryHistory()
  const route = computeCollectiveOffersUrl(filters)
  history.push(route)
  return {
    ...render(
      <Provider store={store}>
        <Router history={history}>
          <CollectiveOffers />
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

jest.mock('apiClient/api', () => ({
  api: {
    listOffers: jest.fn(),
    getCategories: jest.fn().mockResolvedValue(categoriesAndSubcategories),
    getCollectiveOffers: jest.fn(),
    getOfferer: jest.fn(),
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

describe('route CollectiveOffers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
    publicName: string
  }
  let store: Store
  let offersRecap: Offer[]

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
    jest
      .spyOn(api, 'getCollectiveOffers')
      // @ts-ignore FIX ME
      .mockResolvedValue(offersRecap)
  })

  describe('render', () => {
    describe('filters', () => {
      it('should display only selectable categories eligible for EAC on filters', async () => {
        // When
        renderOffers(store)
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

      describe('status filters', () => {
        it('should filter offers given status filter when clicking on "Appliquer"', async () => {
          // Given
          renderOffers(store)
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          fireEvent.click(screen.getByLabelText('Expirée'))
          // When
          fireEvent.click(screen.getByText('Appliquer'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            'EXPIRED',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should indicate that no offers match selected filters', async () => {
          // Given
          jest
            .spyOn(api, 'getCollectiveOffers')
            // @ts-ignore FIX ME
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          renderOffers(store)
          // When
          fireEvent.click(
            await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
          )
          fireEvent.click(screen.getByLabelText('Expirée'))
          fireEvent.click(screen.getByText('Appliquer'))
          // Then
          const noOffersForSearchFiltersText = await screen.findByText(
            'Aucune offre trouvée pour votre recherche'
          )
          expect(noOffersForSearchFiltersText).toBeInTheDocument()
        })

        it('should not display column titles when no offers are returned', async () => {
          // Given
          jest.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])
          // When
          renderOffers(store)

          // Then
          expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
          expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
        })
      })

      describe('when user is admin', () => {
        beforeEach(() => {
          store = configureTestStore({
            data: {
              users: [{ ...currentUser, isAdmin: true }],
            },
            user: {
              initialized: true,
            },
            offers: {
              searchFilters: DEFAULT_SEARCH_FILTERS,
            },
          })
        })
        describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
          it('should reset and disable status filter when venue filter is deselected', async () => {
            // Given
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId,
              status: 'inactive',
            }
            renderOffers(store, filters)
            await waitFor(() =>
              expect(screen.getByDisplayValue(venueName)).toBeInTheDocument()
            )
            fireEvent.change(screen.getByDisplayValue(venueName), {
              target: { value: ALL_VENUES },
            })
            // When
            fireEvent.click(screen.getByText('Lancer la recherche'))
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
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

          it('should not reset or disable status filter when venue filter is deselected while offerer filter is applied', async () => {
            // Given
            const { id: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId,
              status: 'INACTIVE',
              offererId: 'EF',
            }
            renderOffers(store, filters)
            fireEvent.change(await screen.findByDisplayValue(venueName), {
              target: { value: ALL_VENUES },
            })
            // When
            fireEvent.click(screen.getByText('Lancer la recherche'))
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              'EF',
              'INACTIVE',
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should reset and disable status filter when offerer filter is removed', async () => {
            // Given
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-ignore FIX ME
            jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              offererId: offerer.id,
              status: 'INACTIVE',
            }
            renderOffers(store, filters)
            // When
            fireEvent.click(
              await screen.findByAltText('Supprimer le filtre par structure')
            )
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
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

          it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
            // Given
            const { id: venueId } = proVenues[0]
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-ignore FIX ME
            jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              venueId: venueId,
              status: 'INACTIVE',
              offererId: offerer.id,
            }
            renderOffers(store, filters)
            // When
            fireEvent.click(
              await screen.findByAltText('Supprimer le filtre par structure')
            )
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              'INACTIVE',
              venueId,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should enable status filters when venue filter is applied', async () => {
            // Given
            const filters = { venueId: 'IJ' }
            // When
            renderOffers(store, filters)
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            // Given
            const filters = { offererId: 'A4' }
            // When
            renderOffers(store, filters)
            // Then
            const statusFiltersIcon = await screen.findByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })
        })
      })

      describe('on click on search button', () => {
        it('should load offers with written offer name filter', async () => {
          // Given
          renderOffers(store)
          fireEvent.change(
            await screen.findByPlaceholderText('Rechercher par nom d’offre'),
            {
              target: { value: 'Any word' },
            }
          )
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected venue filter', async () => {
          // Given
          renderOffers(store)
          const firstVenueOption = await screen.findByRole('option', {
            name: proVenues[0].name,
          })
          const venueSelect = screen.getByLabelText('Lieu')
          await userEvent.selectOptions(venueSelect, firstVenueOption)
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            undefined,
            undefined,
            undefined,
            proVenues[0].id,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected type filter', async () => {
          // Given
          renderOffers(store)
          const firstTypeOption = await screen.findByRole('option', {
            name: 'Cinéma',
          })
          const typeSelect = screen.getByDisplayValue(
            ALL_CATEGORIES_OPTION.displayName
          )
          await userEvent.selectOptions(typeSelect, firstTypeOption)
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            'CINEMA',
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected period beginning date', async () => {
          // Given
          renderOffers(store)
          await userEvent.click(
            (
              await screen.findAllByPlaceholderText('JJ/MM/AAAA')
            )[0]
          )
          await userEvent.click(screen.getByText('25'))
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-25T00:00:00Z',
            undefined
          )
        })

        it('should load offers with selected period ending date', async () => {
          // Given
          renderOffers(store)
          fireEvent.click(
            (await screen.findAllByPlaceholderText('JJ/MM/AAAA'))[1]
          )
          fireEvent.click(screen.getByText('27'))
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27T23:59:59Z'
          )
        })
      })
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // Given
      const offersRecap = Array.from({ length: 11 }, () => offerFactory())
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offersRecap)
      const { history } = renderOffers(store)
      const nextPageIcon = await screen.findByAltText('page suivante')
      // When
      fireEvent.click(nextPageIcon)
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        page: '2',
      })
    })

    it('should have offer name value when name search value is not an empty string', async () => {
      // Given
      const { history } = renderOffers(store)
      // When
      fireEvent.change(
        await screen.findByPlaceholderText('Rechercher par nom d’offre'),
        {
          target: { value: 'AnyWord' },
        }
      )
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        'nom-ou-isbn': 'AnyWord',
      })
    })

    it('should store search value', async () => {
      // Given
      renderOffers(store)
      const searchInput = await screen.findByPlaceholderText(
        'Rechercher par nom d’offre'
      )
      // When
      fireEvent.change(searchInput, { target: { value: 'search string' } })
      fireEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(api.getCollectiveOffers).toHaveBeenCalledWith(
        'search string',
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      // Given
      const { history } = renderOffers(store)
      // When
      fireEvent.change(
        await screen.findByPlaceholderText('Rechercher par nom d’offre'),
        {
          target: { value: ALL_OFFERS },
        }
      )
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({})
    })

    it('should have venue value when user filters by venue', async () => {
      // Given
      const { history } = renderOffers(store)
      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')
      // When
      await userEvent.selectOptions(venueSelect, firstVenueOption)
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        lieu: proVenues[0].id,
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offersRecap)
      jest.spyOn(api, 'getCategories').mockResolvedValue({
        categories: [
          { id: 'test_id_1', proLabel: 'My test value', isSelectable: true },
          {
            id: 'test_id_2',
            proLabel: 'My second test value',
            isSelectable: true,
          },
        ],
        subcategories: [
          // @ts-ignore FIX ME
          {
            id: 'test_sub_id_1',
            categoryId: 'test_id_1',
            isSelectable: true,
            canBeEducational: true,
          },
          // @ts-ignore FIX ME
          {
            id: 'test_sub_id_2',
            categoryId: 'test_id_2',
            canBeEducational: true,
            isSelectable: true,
          },
        ],
      })
      const { history } = renderOffers(store)
      const firstTypeOption = await screen.findByRole('option', {
        name: 'My test value',
      })
      const typeSelect = screen.getByDisplayValue(
        ALL_CATEGORIES_OPTION.displayName
      )
      // When
      await userEvent.selectOptions(typeSelect, firstTypeOption)
      fireEvent.click(screen.getByText('Lancer la recherche'))
      await waitFor(() => {
        const urlSearchParams = parse(history.location.search.substring(1))

        // Then
        expect(urlSearchParams).toMatchObject({
          categorie: 'test_id_1',
        })
      })
    })

    it('should have status value when user filters by status', async () => {
      // Given
      jest.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        // @ts-ignore FIX ME
        offerFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: 'ACTIVE',
          },
          // @ts-expect-error offerFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      const { history } = renderOffers(store)
      fireEvent.click(
        await screen.findByAltText('Afficher ou masquer le filtre par statut')
      )
      fireEvent.click(screen.getByLabelText('Épuisée'))
      // When
      fireEvent.click(screen.getByText('Appliquer'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        statut: 'epuisee',
      })
    })

    it('should have status value be removed when user ask for all status', async () => {
      // Given
      jest.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
        // @ts-ignore FIX ME
        offerFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: 'ACTIVE',
          },
          // @ts-expect-error offerFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      const { history } = renderOffers(store)
      fireEvent.click(
        await screen.findByAltText('Afficher ou masquer le filtre par statut')
      )
      fireEvent.click(screen.getByLabelText('Tous'))
      // When
      fireEvent.click(screen.getByText('Appliquer'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({})
    })

    it('should have offerer filter when user filters by offerer', async () => {
      // Given
      const filters = { offererId: 'A4' }
      // @ts-ignore FIX ME
      jest.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })
      // When
      renderOffers(store, filters)
      // Then
      const offererFilter = await screen.findByText('La structure')
      expect(offererFilter).toBeInTheDocument()
    })

    it('should have offerer value be removed when user removes offerer filter', async () => {
      // Given
      const filters = { offererId: 'A4' }
      // @ts-ignore FIX ME
      jest.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        name: 'La structure',
      })
      renderOffers(store, filters)
      // When
      fireEvent.click(
        await screen.findByAltText('Supprimer le filtre par structure')
      )
      // Then
      expect(screen.queryByText('La structure')).not.toBeInTheDocument()
    })
  })

  describe('page navigation', () => {
    it('should redirect to individual offers when user clicks on individual offers link', async () => {
      // Given

      jest.spyOn(api, 'getCollectiveOffers').mockResolvedValue(
        // @ts-ignore FIX ME
        offersRecap
      )
      const { history } = renderOffers(store)
      await screen.findByText('Lancer la recherche')
      const individualAudienceLink = screen.getByText('Offres individuelles', {
        selector: 'span',
      })

      // When
      fireEvent.click(individualAudienceLink)

      // Then
      await waitFor(() => {
        expect(history.location.pathname).toBe('/offres')
      })

      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
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

    it('should display next page when clicking on right arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => offerFactory())
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offers)
      renderOffers(store)
      const nextIcon = await screen.findByAltText('page suivante')
      // When
      fireEvent.click(nextIcon)
      // Then
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      await expect(
        screen.findByText(offers[10].name)
      ).resolves.toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => offerFactory())
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offers)
      renderOffers(store)
      const nextIcon = await screen.findByAltText('page suivante')
      const previousIcon = await screen.findByAltText('page précédente')
      fireEvent.click(nextIcon)
      // When
      fireEvent.click(previousIcon)
      // Then
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      await expect(
        screen.findByText(offers[0].name)
      ).resolves.toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    it('should not be able to click on previous arrow when being on the first page', async () => {
      // Given
      const filters = { page: DEFAULT_PAGE }
      // When
      renderOffers(store, filters)
      // Then
      const previousIcon = await screen.findByAltText('page précédente')
      expect(previousIcon.closest('button')).toBeDisabled()
    })

    it('should not be able to click on next arrow when being on the last page', async () => {
      // Given
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offersRecap)
      // When
      renderOffers(store)
      // Then
      const nextIcon = await screen.findByAltText('page suivante')
      expect(nextIcon.closest('button')).toBeDisabled()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () => offerFactory())
      })

      it('should have max number page of 50', async () => {
        // Given
        jest
          .spyOn(api, 'getCollectiveOffers')
          // @ts-ignore FIX ME
          .mockResolvedValueOnce(offersRecap)
        // When
        renderOffers(store)
        // Then
        await expect(
          screen.findByText('Page 1/50')
        ).resolves.toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        // Given
        jest
          .spyOn(api, 'getCollectiveOffers')
          // @ts-ignore FIX ME
          .mockResolvedValueOnce(offersRecap)
        renderOffers(store)
        const nextIcon = await screen.findByAltText('page suivante')
        // When
        for (let i = 1; i < 51; i++) {
          fireEvent.click(nextIcon)
        }
        // Then
        expect(screen.getByText(offersRecap[499].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[500].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      renderOffers(store)

      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName
      )

      await userEvent.selectOptions(venueSelect, firstVenueOption)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      fireEvent.click(screen.getByText('Lancer la recherche'))

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].id,
        undefined,
        undefined,
        undefined,
        undefined
      )

      await screen.findByText('Aucune offre trouvée pour votre recherche')

      fireEvent.click(screen.getByText('afficher toutes les offres'))

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(3)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        3,
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

    it('when clicking on "Réinitialiser les filtres"', async () => {
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-ignore FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      renderOffers(store)

      const venueOptionToSelect = await screen.findByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName
      )

      await userEvent.selectOptions(venueSelect, venueOptionToSelect)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      fireEvent.click(screen.getByText('Lancer la recherche'))
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].id,
        undefined,
        undefined,
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Réinitialiser les filtres'))
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(3)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        3,
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
})
