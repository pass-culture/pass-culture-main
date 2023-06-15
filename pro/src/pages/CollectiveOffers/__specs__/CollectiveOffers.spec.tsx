import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer, TSearchFilters } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOffers from '../CollectiveOffers'
import { collectiveOfferFactory } from '../utils/collectiveOffersFactories'

const renderOffers = async (
  storeOverrides: Store,
  filters: Partial<TSearchFilters> & {
    page?: number
  } = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  renderWithProviders(<CollectiveOffers />, {
    storeOverrides,
    initialRouterEntries: [route],
  })

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
    id: 'JI',
    nonHumanizedId: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    isVirtual: false,
  },
  {
    id: 'JQ',
    nonHumanizedId: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  },
]

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
}))

jest.mock('apiClient/api', () => ({
  api: {
    listOffers: jest.fn(),
    getCategories: jest.fn().mockResolvedValue(categoriesAndSubcategories),
    getCollectiveOffers: jest.fn(),
    getOfferer: jest.fn(),
    getVenues: jest.fn().mockResolvedValue({ venues: proVenues }),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(true),
}))

describe('route CollectiveOffers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
  }
  let store: any
  let offersRecap: Offer[]

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
  })

  describe('render', () => {
    describe('filters', () => {
      it('should display only selectable categories eligible for EAC on filters', async () => {
        // When
        await renderOffers(store)
        screen.getByText('Lancer la recherche')

        // Then
        expect(
          screen.getByRole('option', { name: 'Cinéma' })
        ).toBeInTheDocument()
        expect(
          screen.queryByRole('option', { name: 'Jeux' })
        ).not.toBeInTheDocument()
        expect(
          screen.queryByRole('option', { name: 'Technique' })
        ).not.toBeInTheDocument()
      })

      describe('status filters', () => {
        it('should filter offers given status filter when clicking on "Appliquer"', async () => {
          // Given
          await renderOffers(store)
          await userEvent.click(
            screen.getByAltText('Afficher ou masquer le filtre par statut')
          )
          await userEvent.click(screen.getByLabelText('Expirée'))
          // When
          await userEvent.click(screen.getByText('Appliquer'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            'EXPIRED',
            undefined,
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
            // @ts-expect-error FIX ME
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          await renderOffers(store)
          // When
          await userEvent.click(
            screen.getByAltText('Afficher ou masquer le filtre par statut')
          )
          await userEvent.click(screen.getByLabelText('Expirée'))
          await userEvent.click(screen.getByText('Appliquer'))
          // Then
          const noOffersForSearchFiltersText = screen.getByText(
            'Aucune offre trouvée pour votre recherche'
          )
          expect(noOffersForSearchFiltersText).toBeInTheDocument()
        })

        it('should not display column titles when no offers are returned', async () => {
          // Given
          jest.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])
          // When
          await renderOffers(store)

          // Then
          expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
          expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
        })
      })

      describe('when user is admin', () => {
        beforeEach(() => {
          store = {
            user: {
              initialized: true,
              currentUser: { ...currentUser, isAdmin: true },
            },
            offers: {
              searchFilters: DEFAULT_SEARCH_FILTERS,
            },
          }
        })
        describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
          it('should reset and disable status filter when venue filter is deselected', async () => {
            // Given
            const { nonHumanizedId: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)
            await userEvent.selectOptions(
              screen.getByDisplayValue(venueName),
              ALL_VENUES
            )
            // When
            await userEvent.click(screen.getByText('Lancer la recherche'))
            // Then
            const statusFiltersIcon = screen.getByAltText(
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
              undefined,
              undefined
            )
          })

          it('should not reset or disable status filter when venue filter is deselected while offerer filter is applied', async () => {
            // Given
            const { nonHumanizedId: venueId, name: venueName } = proVenues[0]
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: 'EF',
            }
            await renderOffers(store, filters)
            await userEvent.selectOptions(
              screen.getByDisplayValue(venueName),
              ALL_VENUES
            )
            // When
            await userEvent.click(screen.getByText('Lancer la recherche'))
            // Then
            const statusFiltersIcon = screen.getByAltText(
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
              undefined,
              undefined
            )
          })

          it('should reset and disable status filter when offerer filter is removed', async () => {
            // Given
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-expect-error FIX ME
            jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              offererId: offerer.id,
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)
            // When
            await userEvent.click(screen.getByTestId('remove-offerer-filter'))
            // Then
            const statusFiltersIcon = screen.getByAltText(
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
              undefined,
              undefined
            )
          })

          it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
            // Given
            const { nonHumanizedId: venueId } = proVenues[0]
            const offerer = { name: 'La structure', id: 'EF' }
            // @ts-expect-error FIX ME
            jest.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: offerer.id,
            }
            await renderOffers(store, filters)
            // When
            await userEvent.click(screen.getByTestId('remove-offerer-filter'))
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
            expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              'INACTIVE',
              venueId.toString(),
              undefined,
              undefined,
              undefined,
              undefined,
              undefined
            )
          })

          it('should enable status filters when venue filter is applied', async () => {
            // Given
            const filters = { venueId: proVenues[0].nonHumanizedId.toString() }
            // When
            await renderOffers(store, filters)
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            // Given
            const filters = { offererId: 'A4' }
            // When
            await renderOffers(store, filters)
            // Then
            const statusFiltersIcon = screen.getByAltText(
              'Afficher ou masquer le filtre par statut'
            )
            expect(statusFiltersIcon.closest('button')).not.toBeDisabled()
          })
        })
      })

      describe('on click on search button', () => {
        it('should load offers with written offer name filter', async () => {
          // Given
          await renderOffers(store)
          await userEvent.type(
            screen.getByPlaceholderText('Rechercher par nom d’offre'),
            'Any word'
          )
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
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

        it('should store search value', async () => {
          // Given
          await renderOffers(store)
          const searchInput = screen.getByPlaceholderText(
            'Rechercher par nom d’offre'
          )
          // When
          await userEvent.type(searchInput, 'search string')
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'search string',
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

        it('should load offers with selected venue filter', async () => {
          // Given
          await renderOffers(store)
          const firstVenueOption = screen.getByRole('option', {
            name: proVenues[0].name,
          })
          const venueSelect = screen.getByLabelText('Lieu')
          await userEvent.selectOptions(venueSelect, firstVenueOption)
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            undefined,
            undefined,
            undefined,
            proVenues[0].nonHumanizedId.toString(),
            undefined,
            undefined,
            undefined,
            undefined,
            undefined
          )
        })

        it('should load offers with selected type filter', async () => {
          // Given
          await renderOffers(store)
          const firstTypeOption = screen.getByRole('option', {
            name: 'Cinéma',
          })
          const typeSelect = screen.getByDisplayValue(
            ALL_CATEGORIES_OPTION.label
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
            undefined,
            undefined
          )
        })

        it('should load offers with selected period beginning date', async () => {
          await renderOffers(store)

          await userEvent.type(
            screen.getByLabelText('Début de la période'),
            '25/12/2020'
          )

          await userEvent.click(screen.getByText('Lancer la recherche'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-25T00:00:00Z',
            undefined,
            undefined
          )
        })

        it('should load offers with selected period ending date', async () => {
          await renderOffers(store)
          await userEvent.type(
            screen.getByLabelText('Fin de la période'),
            '27/12/2020'
          )

          await userEvent.click(screen.getByText('Lancer la recherche'))

          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27T23:59:59Z',
            undefined
          )
        })
        it('should load offers with selected offer type', async () => {
          // Given
          await renderOffers(store)
          const offerTypeSelect = screen.getByLabelText('Type de l’offre')
          await userEvent.selectOptions(offerTypeSelect, 'template')
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
            undefined,
            undefined,
            'template'
          )
        })
      })
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => collectiveOfferFactory())
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByAltText('Page suivante')
      // When
      await userEvent.click(nextIcon)
      // Then
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () => collectiveOfferFactory())
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByAltText('Page suivante')
      const previousIcon = screen.getByAltText('Page précédente')
      await userEvent.click(nextIcon)
      // When
      await userEvent.click(previousIcon)
      // Then
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () =>
          collectiveOfferFactory()
        )
      })

      it('should have max number page of 50', async () => {
        // Given
        jest
          .spyOn(api, 'getCollectiveOffers')
          // @ts-expect-error FIX ME
          .mockResolvedValueOnce(offersRecap)
        // When
        await renderOffers(store)
        // Then
        expect(screen.getByText('Page 1/50')).toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        // Given
        jest
          .spyOn(api, 'getCollectiveOffers')
          // @ts-expect-error FIX ME
          .mockResolvedValueOnce(offersRecap)
        await renderOffers(store)
        const nextIcon = screen.getByAltText('Page suivante')
        // When
        for (let i = 1; i < 51; i++) {
          await userEvent.click(nextIcon)
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
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(store)

      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

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
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Lancer la recherche'))

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].nonHumanizedId.toString(),
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )

      screen.getByText('Aucune offre trouvée pour votre recherche')

      await userEvent.click(screen.getByText('afficher toutes les offres'))

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
        undefined,
        undefined
      )
    })

    it('when clicking on "Réinitialiser les filtres"', async () => {
      jest
        .spyOn(api, 'getCollectiveOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      await renderOffers(store)

      const venueOptionToSelect = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

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
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Lancer la recherche'))
      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(2)
      expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
        2,
        undefined,
        undefined,
        undefined,
        proVenues[0].nonHumanizedId.toString(),
        undefined,
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
        undefined,
        undefined
      )
    })
  })
})
