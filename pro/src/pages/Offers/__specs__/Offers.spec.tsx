import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_CREATION_MODES,
  ALL_VENUES,
  ALL_VENUES_OPTION,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import {
  defaultGetOffererResponseModel,
  getVenueListItemFactory,
  listOffersOfferResponseModelFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersRoute } from '../../../pages/Offers/OffersRoute'

const categoriesAndSubcategories = {
  categories: [
    { id: 'CINEMA', proLabel: 'Cinéma', isSelectable: true },
    { id: 'JEU', proLabel: 'Jeux', isSelectable: true },
    { id: 'TECHNIQUE', proLabel: 'Technique', isSelectable: false },
  ],
  subcategories: [],
}

const proVenues = [
  getVenueListItemFactory({
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    publicName: undefined,
    isVirtual: false,
  }),
  getVenueListItemFactory({
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  }),
]

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
  vi.clearAllMocks()
}

vi.mock('repository/venuesService', async () => ({
  ...((await vi.importActual('repository/venuesService')) ?? {}),
}))

vi.mock('utils/date', async () => ({
  ...((await vi.importActual('utils/date')) ?? {}),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

describe('route Offers', () => {
  let currentUser: {
    id: string
    isAdmin: boolean
    name: string
  }
  let store: any
  let offersRecap: ListOffersOfferResponseModel[]

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
    }
    offersRecap = [
      listOffersOfferResponseModelFactory({ customVenue: proVenues[0] }),
    ]
    vi.spyOn(api, 'listOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce(
      categoriesAndSubcategories
    )
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
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

          const statusFiltersButton = screen.getByRole('button', {
            name: /Afficher ou masquer le filtre par statut/,
          })
          expect(statusFiltersButton).toHaveAttribute(
            'aria-controls',
            'offer-status-filters-modal'
          )
          expect(statusFiltersButton).toHaveAttribute('aria-expanded', 'false')
          await userEvent.click(statusFiltersButton)
          expect(statusFiltersButton).toHaveAttribute('aria-expanded', 'true')

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
          await renderOffers(store)

          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Brouillon'))

          await userEvent.click(screen.getByText('Appliquer'))

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
          vi.spyOn(api, 'listOffers')
            .mockResolvedValueOnce(offersRecap)
            .mockResolvedValueOnce([])
          await renderOffers(store)

          await userEvent.click(
            screen.getByRole('button', {
              name: 'Statut Afficher ou masquer le filtre par statut',
            })
          )
          await userEvent.click(screen.getByLabelText('Expirée'))
          await userEvent.click(screen.getByText('Appliquer'))

          const noOffersForSearchFiltersText = screen.getByText(
            'Aucune offre trouvée pour votre recherche'
          )
          expect(noOffersForSearchFiltersText).toBeInTheDocument()
        })

        it('should not display column titles when no offers are returned', async () => {
          vi.spyOn(api, 'listOffers').mockResolvedValueOnce([])

          await renderOffers(store)

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
          }
        })

        describe('status filter can only be used with an offerer or a venue filter for performance reasons', () => {
          it('should reset and disable status filter when venue filter is deselected', async () => {
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

            await userEvent.click(screen.getByText('Rechercher'))

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

            await userEvent.click(screen.getByText('Rechercher'))

            expect(
              screen.getByRole('button', {
                name: /Afficher ou masquer le filtre par statut/,
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
            const offerer = {
              ...defaultGetOffererResponseModel,
              name: 'La structure',
              id: 25,
            }

            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              offererId: offerer.id.toString(),
              status: OfferStatus.INACTIVE,
            }
            await renderOffers(store, filters)

            await userEvent.click(screen.getByTestId('remove-offerer-filter'))

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
            const { id: venueId } = proVenues[0]
            const offerer = {
              ...defaultGetOffererResponseModel,
              name: 'La structure',
              id: 65,
            }

            vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
            const filters = {
              venueId: venueId.toString(),
              status: OfferStatus.INACTIVE,
              offererId: offerer.id.toString(),
            }
            await renderOffers(store, filters)

            await userEvent.click(screen.getByTestId('remove-offerer-filter'))

            expect(
              screen.getByRole('button', {
                name: /Afficher ou masquer le filtre par statut/,
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
            const filters = { venueId: 'IJ' }

            await renderOffers(store, filters)

            expect(
              screen.getByRole('button', {
                name: 'Statut Afficher ou masquer le filtre par statut',
              })
            ).not.toBeDisabled()
          })

          it('should enable status filters when offerer filter is applied', async () => {
            const filters = { offererId: 'A4' }

            await renderOffers(store, filters)

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
          await renderOffers(store)
          await userEvent.type(
            screen.getByPlaceholderText(
              'Rechercher par nom d’offre ou par EAN-13'
            ),
            'Any word'
          )

          await userEvent.click(screen.getByText('Rechercher'))

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
          await renderOffers(store)
          const firstVenueOption = screen.getByRole('option', {
            name: proVenues[0].name,
          })
          const venueSelect = screen.getByLabelText('Lieu')
          await userEvent.selectOptions(venueSelect, firstVenueOption)

          await userEvent.click(screen.getByText('Rechercher'))

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
          await renderOffers(store)
          const firstTypeOption = screen.getByRole('option', {
            name: 'Cinéma',
          })
          const typeSelect = screen.getByDisplayValue(
            ALL_CATEGORIES_OPTION.label
          )
          await userEvent.selectOptions(typeSelect, firstTypeOption)

          await userEvent.click(screen.getByText('Rechercher'))

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
          await renderOffers(store)
          const creationModeSelect = screen.getByDisplayValue('Tous')
          const importedCreationMode = CREATION_MODES_OPTIONS[2].value
          await userEvent.selectOptions(
            creationModeSelect,
            String(importedCreationMode)
          )

          await userEvent.click(screen.getByText('Rechercher'))

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

          await userEvent.click(screen.getByText('Rechercher'))

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
          await userEvent.click(screen.getByText('Rechercher'))

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
      const offersRecap = Array.from({ length: 11 }, () =>
        listOffersOfferResponseModelFactory()
      )
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offersRecap)
      await renderOffers(store)
      const nextPageIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextPageIcon)

      expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    })

    it('should store search value', async () => {
      await renderOffers(store)
      const searchInput = screen.getByPlaceholderText(
        'Rechercher par nom d’offre ou par EAN-13'
      )

      await userEvent.type(searchInput, 'search string')
      await userEvent.click(screen.getByText('Rechercher'))

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
      await renderOffers(store)

      await userEvent.clear(
        screen.getByPlaceholderText('Rechercher par nom d’offre ou par EAN-13')
      )
      await userEvent.click(screen.getByText('Rechercher'))

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
      await renderOffers(store)
      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })
      const venueSelect = screen.getByLabelText('Lieu')

      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Rechercher'))

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
      vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
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

      await userEvent.selectOptions(typeSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Rechercher'))

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
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce([
        listOffersOfferResponseModelFactory({
          customOffer: {
            status: OfferStatus.ACTIVE,
          },
          customStocksList: [],
        }),
      ])

      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Épuisée'))
      await userEvent.click(screen.getByText('Appliquer'))

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
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce([
        listOffersOfferResponseModelFactory({
          customOffer: {
            status: OfferStatus.ACTIVE,
          },
          customStocksList: [],
        }),
      ])
      await renderOffers(store)
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Statut Afficher ou masquer le filtre par statut',
        })
      )
      await userEvent.click(screen.getByLabelText('Toutes'))

      await userEvent.click(screen.getByText('Appliquer'))

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
      const id = 654

      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        ...defaultGetOffererResponseModel,
        name: 'La structure',
      })
      const filters = { offererId: id.toString() }

      await renderOffers(store, filters)

      const offererFilter = screen.getByText('La structure')
      expect(offererFilter).toBeInTheDocument()
    })

    it('should have offerer value be removed when user removes offerer filter', async () => {
      const id = 654
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        ...defaultGetOffererResponseModel,
        name: 'La structure',
        id,
      })
      const filters = { offererId: id.toString() }
      await renderOffers(store, filters)

      await userEvent.click(screen.getByTestId('remove-offerer-filter'))

      expect(screen.queryByText('La structure')).not.toBeInTheDocument()
    })

    it('should have creation mode value when user filters by creation mode', async () => {
      await renderOffers(store)

      await userEvent.selectOptions(screen.getByDisplayValue('Tous'), 'manual')
      await userEvent.click(screen.getByText('Rechercher'))

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
      await renderOffers(store)
      const searchButton = screen.getByText('Rechercher')
      await userEvent.selectOptions(screen.getByDisplayValue('Tous'), 'manual')
      await userEvent.click(searchButton)

      await userEvent.selectOptions(
        screen.getByDisplayValue('Manuel'),
        ALL_CREATION_MODES
      )
      await userEvent.click(searchButton)

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
      vi.spyOn(api, 'listOffers').mockResolvedValue(offersRecap)
      await renderOffers(store)
      screen.getByText('Rechercher')
      const collectiveAudienceLink = screen.getByText('Offres collectives', {
        selector: 'span',
      })

      await userEvent.click(collectiveAudienceLink)

      expect(screen.getByText('Offres collectives')).toBeInTheDocument()
    })

    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        listOffersOfferResponseModelFactory()
      )
      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextIcon)

      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByLabelText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        listOffersOfferResponseModelFactory()
      )

      vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offers)
      await renderOffers(store)
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })
      const previousIcon = screen.getByRole('button', {
        name: 'Page précédente',
      })
      await userEvent.click(nextIcon)

      await userEvent.click(previousIcon)

      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 501 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 501 }, () =>
          listOffersOfferResponseModelFactory({ customStocksList: [] })
        )
      })

      it('should have max number page of 50', async () => {
        vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderOffers(store)

        expect(screen.getByText('Page 1/50')).toBeInTheDocument()
      })

      it('should not display the 501st offer', async () => {
        vi.spyOn(api, 'listOffers').mockResolvedValueOnce(offersRecap)
        await renderOffers(store)
        const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

        for (let i = 1; i < 51; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[499].name)).toBeInTheDocument()
        expect(
          screen.queryByLabelText(offersRecap[500].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      vi.spyOn(api, 'listOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
      await renderOffers(store)

      const firstVenueOption = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, firstVenueOption)
      await userEvent.click(screen.getByText('Rechercher'))

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

      await userEvent.click(screen.getByText('Afficher toutes les offres'))

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
      vi.spyOn(api, 'listOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      await renderOffers(store)

      const venueOptionToSelect = screen.getByRole('option', {
        name: proVenues[0].name,
      })

      const venueSelect = screen.getByDisplayValue(ALL_VENUES_OPTION.label)

      await userEvent.selectOptions(venueSelect, venueOptionToSelect)
      await userEvent.click(screen.getByText('Rechercher'))

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
