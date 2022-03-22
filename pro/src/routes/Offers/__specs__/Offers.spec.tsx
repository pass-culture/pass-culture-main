import '@testing-library/jest-dom'
import { parse } from 'querystring'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import type { Store } from 'redux'

import { api } from 'api/v1/api'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import {
  ALL_OFFERS,
  ALL_CATEGORIES_OPTION,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  CREATION_MODES_FILTERS,
  DEFAULT_CREATION_MODE,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer, SearchFilters } from 'core/Offers/types'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { offerFactory } from 'utils/apiFactories'

import Offers from '../Offers'

const renderOffers = (
  store: Store,
  filters: Partial<SearchFilters> & { page?: number } = DEFAULT_SEARCH_FILTERS
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
  subcategories: [],
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

jest.mock('repository/pcapi/pcapi', () => ({
  loadCategories: jest.fn().mockResolvedValue(categoriesAndSubcategories),
}))

jest.mock('api/v1/api', () => ({
  api: {
    getOffersListOffers: jest.fn(),
    getOfferersGetOfferer: jest.fn(),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

describe('route Offers', () => {
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
    ;(api.getOffersListOffers as jest.Mock).mockResolvedValue(offersRecap)
  })

  describe('render', () => {
    describe('filters', () => {
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
          expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
          ;(api.getOffersListOffers as jest.Mock)
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
          ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce([])
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
            expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
            expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
            ;(api.getOfferersGetOfferer as jest.Mock).mockResolvedValue(offerer)
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
            expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
            ;(api.getOfferersGetOfferer as jest.Mock).mockResolvedValue(offerer)
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
            expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
            await screen.findByPlaceholderText(
              'Rechercher par nom d’offre ou par ISBN'
            ),
            {
              target: { value: 'Any word' },
            }
          )
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getOffersListOffers).toHaveBeenCalledWith(
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
          userEvent.selectOptions(venueSelect, firstVenueOption)
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getOffersListOffers).toHaveBeenCalledWith(
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
          userEvent.selectOptions(typeSelect, firstTypeOption)
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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

        it('should load offers with selected creation mode filter', async () => {
          // Given
          renderOffers(store)
          const creationModeSelect = await screen.findByDisplayValue(
            DEFAULT_CREATION_MODE.displayName
          )
          const importedCreationMode = CREATION_MODES_FILTERS[1].id
          fireEvent.change(creationModeSelect, {
            target: { value: importedCreationMode },
          })
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            'imported',
            undefined,
            undefined
          )
        })

        it('should load offers with selected period beginning date', async () => {
          // Given
          renderOffers(store)
          fireEvent.click(
            (await screen.findAllByPlaceholderText('JJ/MM/AAAA'))[0]
          )
          fireEvent.click(screen.getByText('25'))
          // When
          fireEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
          expect(api.getOffersListOffers).toHaveBeenLastCalledWith(
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
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(offersRecap)
      const { history } = renderOffers(store)
      const nextPageIcon = await screen.findByAltText(
        'Aller à la page suivante'
      )
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
        await screen.findByPlaceholderText(
          'Rechercher par nom d’offre ou par ISBN'
        ),
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
        'Rechercher par nom d’offre ou par ISBN'
      )
      // When
      fireEvent.change(searchInput, { target: { value: 'search string' } })
      fireEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(api.getOffersListOffers).toHaveBeenCalledWith(
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
        await screen.findByPlaceholderText(
          'Rechercher par nom d’offre ou par ISBN'
        ),
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
      userEvent.selectOptions(venueSelect, firstVenueOption)
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        lieu: proVenues[0].id,
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      ;(pcapi.loadCategories as jest.Mock).mockResolvedValue({
        categories: [
          { id: 'test_id_1', proLabel: 'My test value', isSelectable: true },
          {
            id: 'test_id_2',
            proLabel: 'My second test value',
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
      userEvent.selectOptions(typeSelect, firstTypeOption)
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        categorie: 'test_id_1',
      })
    })

    it('should have status value when user filters by status', async () => {
      // Given
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce([
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
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce([
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
      ;(api.getOfferersGetOfferer as jest.Mock).mockResolvedValueOnce({
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
      ;(api.getOfferersGetOfferer as jest.Mock).mockResolvedValueOnce({
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

    it('should have creation mode value when user filters by creation mode', async () => {
      // Given
      const { history } = renderOffers(store)
      // When
      fireEvent.change(await screen.findByDisplayValue('Tous les modes'), {
        target: { value: 'manual' },
      })
      fireEvent.click(screen.getByText('Lancer la recherche'))
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({
        creation: 'manuelle',
      })
    })

    it('should have creation mode value be removed when user ask for all creation modes', async () => {
      // Given
      const { history } = renderOffers(store)
      const searchButton = await screen.findByText('Lancer la recherche')
      fireEvent.change(screen.getByDisplayValue('Tous les modes'), {
        target: { value: 'manual' },
      })
      fireEvent.click(searchButton)
      // When
      fireEvent.change(screen.getByDisplayValue('Manuelle'), {
        target: { value: DEFAULT_CREATION_MODE.id },
      })
      fireEvent.click(searchButton)
      const urlSearchParams = parse(history.location.search.substring(1))
      // Then
      expect(urlSearchParams).toMatchObject({})
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => offerFactory())
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(offers)
      renderOffers(store)
      const nextIcon = await screen.findByAltText('Aller à la page suivante')
      // When
      fireEvent.click(nextIcon)
      // Then
      expect(api.getOffersListOffers).toHaveBeenCalledTimes(1)
      await expect(
        screen.findByText(offers[10].name)
      ).resolves.toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => offerFactory())
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(offers)
      renderOffers(store)
      const nextIcon = await screen.findByAltText('Aller à la page suivante')
      const previousIcon = await screen.findByAltText(
        'Aller à la page précédente'
      )
      fireEvent.click(nextIcon)
      // When
      fireEvent.click(previousIcon)
      // Then
      expect(api.getOffersListOffers).toHaveBeenCalledTimes(1)
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
      const previousIcon = await screen.findByAltText(
        'Aller à la page précédente'
      )
      expect(previousIcon.closest('button')).toBeDisabled()
    })

    it('should not be able to click on next arrow when being on the last page', async () => {
      // Given
      ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(offersRecap)
      // When
      renderOffers(store)
      // Then
      const nextIcon = await screen.findByAltText('Aller à la page suivante')
      expect(nextIcon.closest('button')).toBeDisabled()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () => offerFactory())
      })

      it('should have max number page of 50', async () => {
        // Given
        ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(
          offersRecap
        )
        // When
        renderOffers(store)
        // Then
        await expect(
          screen.findByText('Page 1/50')
        ).resolves.toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        // Given
        ;(api.getOffersListOffers as jest.Mock).mockResolvedValueOnce(
          offersRecap
        )
        renderOffers(store)
        const nextIcon = await screen.findByAltText('Aller à la page suivante')
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
      ;(api.getOffersListOffers as jest.Mock)
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      renderOffers(store)

      const firstVenueOption = await screen.findByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName
      )

      userEvent.selectOptions(venueSelect, firstVenueOption)

      expect(api.getOffersListOffers).toHaveBeenCalledTimes(1)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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

      expect(api.getOffersListOffers).toHaveBeenCalledTimes(2)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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

      expect(api.getOffersListOffers).toHaveBeenCalledTimes(3)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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
      ;(api.getOffersListOffers as jest.Mock)
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      renderOffers(store)

      const venueOptionToSelect = await screen.findByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(
        ALL_VENUES_OPTION.displayName
      )

      userEvent.selectOptions(venueSelect, venueOptionToSelect)

      expect(api.getOffersListOffers).toHaveBeenCalledTimes(1)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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
      expect(api.getOffersListOffers).toHaveBeenCalledTimes(2)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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

      fireEvent.click(screen.getByText('Réinitialiser les filtres'))
      expect(api.getOffersListOffers).toHaveBeenCalledTimes(3)
      expect(api.getOffersListOffers).toHaveBeenNthCalledWith(
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
