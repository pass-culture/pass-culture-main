import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_CREATION_MODES,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offer, SearchFiltersParams } from 'core/Offers/types'
import { computeOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import { individualOfferFactory } from 'screens/Offers/utils/individualOffersFactories'
import { GetIndividualOfferFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffersRoute from '../../../pages/Offers/OffersRoute'

const renderOffers = async (
  storeOverrides: any,
  filters: Partial<SearchFiltersParams> & {
    page?: number
    audience?: Audience
  } = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeOffersUrl(filters)
  renderWithProviders(
    <Routes>
      <Route path="/offres" element={<OffersRoute />} />
      <Route
        path="/offres/collectives"
        element={<div>Offres collectives</div>}
      />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: [route],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
  jest.clearAllMocks()
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
    getCategories: vi.fn().mockResolvedValue(categoriesAndSubcategories),
    listOffers: vi.fn(),
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

describe('route Offers', () => {
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
    offersRecap = [individualOfferFactory()]
    // @ts-expect-error FIX ME
    vi.spyOn(api, 'listOffers').mockResolvedValue(offersRecap)
  })

  describe('render', () => {
    describe('filters', () => {
      it('should display only selectable categories on filters', async () => {
        await renderOffers(store)

        expect(
          screen.getByRole('option', { name: 'Cinéma' })
        ).toBeInTheDocument()
        expect(screen.getByRole('option', { name: 'Jeux' })).toBeInTheDocument()
        expect(
          screen.queryByRole('option', { name: 'Technique' })
        ).not.toBeInTheDocument()
      })

      describe('status filters', () => {
        it('should filter offers given status filter when clicking on "Appliquer"', async () => {
          await renderOffers(store)

          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Expirée'))
          await userEvent.click(screen.getByText('Appliquer'))

          expect(api.listOffers).toHaveBeenLastCalledWith(
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

        it('should filter draft offers given status filter when clicking on "Appliquer"', async () => {
          // Given
          await renderOffers(store)

          // When
          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Brouillon'))

          await userEvent.click(screen.getByText('Appliquer'))

          // Then
          expect(api.listOffers).toHaveBeenCalledTimes(1)
          expect(api.listOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            'DRAFT',
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
            .spyOn(api, 'listOffers')
            // @ts-expect-error FIX ME
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          await renderOffers(store)
          // When
          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
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
          vi.spyOn(api, 'listOffers').mockResolvedValueOnce([])
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
            const { id: venueId, name: venueName } = proVenues[0]
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
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).toBeDisabled()
            expect(api.listOffers).toHaveBeenLastCalledWith(
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
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
            expect(api.listOffers).toHaveBeenLastCalledWith(
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
            // @ts-expect-error FIX ME
            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              offererId: offerer.id,
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)
            // When
            await userEvent.click(screen.getByTestId('remove-offerer-filter'))
            // Then
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).toBeDisabled()
            expect(api.listOffers).toHaveBeenLastCalledWith(
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
            // @ts-expect-error FIX ME
            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: offerer.id,
            }
            await renderOffers(store, filters)
            // When
            await userEvent.click(screen.getByTestId('remove-offerer-filter'))
            // Then
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
            expect(api.listOffers).toHaveBeenLastCalledWith(
              undefined,
              undefined,
              'INACTIVE',
              venueId.toString(),
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
            await renderOffers(store, filters)
            // Then
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            // Given
            const filters = { offererId: 'A4' }
            // When
            await renderOffers(store, filters)
            // Then
            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
          })
        })
      })

      describe('on click on search button', () => {
        it('should load offers with written offer name filter', async () => {
          // Given
          await renderOffers(store)
          await userEvent.type(
            screen.getByPlaceholderText(
              'Rechercher par nom d’offre ou par EAN-13'
            ),
            'Any word'
          )
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.listOffers).toHaveBeenCalledWith(
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
          await renderOffers(store)
          const firstVenueOption = screen.getByRole('option', {
            name: proVenues[0].name,
          })
          const venueSelect = screen.getByLabelText('Lieu')
          await userEvent.selectOptions(venueSelect, firstVenueOption)
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.listOffers).toHaveBeenCalledWith(
            undefined,
            undefined,
            undefined,
            proVenues[0].id.toString(),
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
          expect(api.listOffers).toHaveBeenLastCalledWith(
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
          await renderOffers(store)
          const creationModeSelect = screen.getByDisplayValue('Tous')
          const importedCreationMode = CREATION_MODES_OPTIONS[2].value
          await userEvent.selectOptions(
            creationModeSelect,
            String(importedCreationMode)
          )
          // When
          await userEvent.click(screen.getByText('Lancer la recherche'))
          // Then
          expect(api.listOffers).toHaveBeenLastCalledWith(
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
          await renderOffers(store)

          await userEvent.type(
            screen.getByLabelText('Début de la période'),
            '2020-12-25'
          )

          await userEvent.click(screen.getByText('Lancer la recherche'))

          expect(api.listOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-25',
            undefined
          )
        })

        it('should load offers with selected period ending date', async () => {
          await renderOffers(store)

          await userEvent.type(
            screen.getByLabelText('Fin de la période'),
            '2020-12-27'
          )
          await userEvent.click(screen.getByText('Lancer la recherche'))

          expect(api.listOffers).toHaveBeenLastCalledWith(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27'
          )
        })
      })
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      // Given
      const offersRecap = Array.from({ length: 11 }, () =>
        individualOfferFactory()
      )
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers(store)
      const nextPageIcon = screen.getByRole('button', { name: 'Page suivante' })
      // When
      await userEvent.click(nextPageIcon)

      // Then
      expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    })

    it('should store search value', async () => {
      // Given
      await renderOffers(store)
      const searchInput = screen.getByPlaceholderText(
        'Rechercher par nom d’offre ou par EAN-13'
      )
      // When
      await userEvent.type(searchInput, 'search string')
      await userEvent.click(screen.getByText('Lancer la recherche'))
      // Then
      expect(api.listOffers).toHaveBeenCalledWith(
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
      await renderOffers(store)
      // When
      await userEvent.clear(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par EAN-13')
      )
      await userEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(api.listOffers).toHaveBeenCalledWith(
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
      expect(api.listOffers).toHaveBeenCalledWith(
        undefined,
        undefined,
        undefined,
        proVenues[0].id.toString(),
        undefined,
        undefined,
        undefined,
        undefined
      )
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      // Given
      vi.spyOn(api, 'getCategories').mockResolvedValue({
        categories: [
          { id: 'test_id_1', proLabel: 'My test value', isSelectable: true },
          {
            id: 'test_id_2',
            proLabel: 'My second test value',
            isSelectable: true,
          },
        ],
        subcategories: [],
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
      expect(api.listOffers).toHaveBeenCalledWith(
        undefined,
        undefined,
        undefined,
        undefined,
        'test_id_1',
        undefined,
        undefined,
        undefined
      )
    })

    it('should have status value when user filters by status', async () => {
      // Given

      vi.spyOn(api, 'listOffers').mockResolvedValueOnce([
        // @ts-expect-error FIX ME
        GetIndividualOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error individualOfferFactory is not typed and null throws an error but is accepted by the function
          null
        ),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Épuisée'))
      // When
      await userEvent.click(screen.getByText('Appliquer'))

      // Then
      expect(api.listOffers).toHaveBeenCalledWith(
        undefined,
        undefined,
        'SOLD_OUT',
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })

    it('should have status value be removed when user ask for all status', async () => {
      // Given
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce([
        // @ts-expect-error FIX ME
        GetIndividualOfferFactory(
          {
            id: 'KE',
            availabilityMessage: 'Pas de stock',
            status: OfferStatus.ACTIVE,
          },
          // @ts-expect-error individualOfferFactory is not typed and null throws an error but is accepted by the function
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
      expect(api.listOffers).toHaveBeenCalledWith(
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

    it('should have creation mode value when user filters by creation mode', async () => {
      // Given
      await renderOffers(store)
      // When
      await userEvent.selectOptions(screen.getByDisplayValue('Tous'), 'manual')
      await userEvent.click(screen.getByText('Lancer la recherche'))

      // Then
      expect(api.listOffers).toHaveBeenCalledWith(
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        'manual',
        undefined,
        undefined
      )
    })

    it('should have creation mode value be removed when user ask for all creation modes', async () => {
      // Given
      await renderOffers(store)
      const searchButton = screen.getByText('Lancer la recherche')
      await userEvent.selectOptions(screen.getByDisplayValue('Tous'), 'manual')
      await userEvent.click(searchButton)
      // When
      await userEvent.selectOptions(
        screen.getByDisplayValue('Manuel'),
        ALL_CREATION_MODES
      )
      await userEvent.click(searchButton)

      // Then
      expect(api.listOffers).toHaveBeenCalledWith(
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

  describe('page navigation', () => {
    it('should redirect to collective offers when user click on collective offer link', async () => {
      // Given
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'listOffers').mockResolvedValue(offersRecap)
      await renderOffers(store)
      screen.getByText('Lancer la recherche')
      const collectiveAudienceLink = screen.getByText('Offres collectives', {
        selector: 'span',
      })

      // When
      await userEvent.click(collectiveAudienceLink)

      // Then
      expect(screen.getByText('Offres collectives')).toBeInTheDocument()
    })

    it('should display next page when clicking on right arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () =>
        GetIndividualOfferFactory()
      )
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

      // When
      await userEvent.click(nextIcon)

      // Then
      expect(screen.getByText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      // Given
      const offers = Array.from({ length: 11 }, () =>
        GetIndividualOfferFactory()
      )
      // @ts-expect-error FIX ME
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })
      const previousIcon = screen.getByRole('button', {
        name: 'Page précédente',
      })
      await userEvent.click(nextIcon)

      // When
      await userEvent.click(previousIcon)

      // Then
      expect(screen.getByText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () =>
          individualOfferFactory()
        )
      })

      it('should have max number page of 50', async () => {
        // Given
        jest
          .spyOn(api, 'listOffers')
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
          .spyOn(api, 'listOffers')
          // @ts-expect-error FIX ME
          .mockResolvedValueOnce(offersRecap)
        await renderOffers(store)
        const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

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
        .spyOn(api, 'listOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(store)

      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Lancer la recherche'))

      expect(api.listOffers).toHaveBeenCalledTimes(1)
      expect(api.listOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        proVenues[0].id.toString(),
        undefined,
        undefined,
        undefined,
        undefined
      )

      screen.getByText('Aucune offre trouvée pour votre recherche')

      await userEvent.click(screen.getByText('afficher toutes les offres'))

      expect(api.listOffers).toHaveBeenCalledTimes(2)
      expect(api.listOffers).toHaveBeenNthCalledWith(
        2,
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
        .spyOn(api, 'listOffers')
        // @ts-expect-error FIX ME
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      await renderOffers(store)

      const venueOptionToSelect = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, venueOptionToSelect)
      await userEvent.click(screen.getByText('Lancer la recherche'))

      expect(api.listOffers).toHaveBeenCalledTimes(1)
      expect(api.listOffers).toHaveBeenNthCalledWith(
        1,
        undefined,
        undefined,
        undefined,
        proVenues[0].id.toString(),
        undefined,
        undefined,
        undefined,
        undefined
      )

      await userEvent.click(screen.getByText('Réinitialiser les filtres'))
      expect(api.listOffers).toHaveBeenCalledTimes(2)
      expect(api.listOffers).toHaveBeenNthCalledWith(
        2,
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
