import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { beforeEach, expect } from 'vitest'

import { api, apiNew } from '@/apiClient/api'
import {
  type GetVenueAddressResponseModel,
  type ListOffersOfferResponseModel,
  type ListOffersQueryModel,
  OfferStatus,
} from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import type { Audience } from '@/commons/core/shared/types'
import * as useAccessibleScrollModule from '@/commons/hooks/useAccessibleScroll'
import {
  defaultGetOffererResponseModel,
  listOffersOfferFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  venueAddressFactory,
} from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { IndividualOffersFilters } from './common/types'
import { IndividualOffers } from './IndividualOffers'

const makeQuery = (
  overrides: Partial<ListOffersQueryModel> = {}
): ListOffersQueryModel => ({
  nameOrIsbn: undefined,
  venueId: 2,
  categoryId: undefined,
  status: undefined,
  creationMode: undefined,
  periodBeginningDate: undefined,
  periodEndingDate: undefined,
  offererAddressId: undefined,
  ...overrides,
})

const categoriesAndSubcategories = {
  categories: [
    { id: 'CINEMA', proLabel: 'Cinéma', isSelectable: true },
    { id: 'JEU', proLabel: 'Jeux', isSelectable: true },
    { id: 'TECHNIQUE', proLabel: 'Technique', isSelectable: false },
  ],
  subcategories: [],
}

const proVenues = [
  makeVenueListItem({
    id: 1,
    name: 'Venue Name',
    offererName: 'Mon offerer',
    publicName: 'Venue Public Name',
  }),
  makeVenueListItem({
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
  }),
]

const venueAddress: GetVenueAddressResponseModel[] = [
  venueAddressFactory(1, {
    city: 'London',
  }),
  venueAddressFactory(1, {
    city: 'New York',
  }),
]

const LABELS = {
  nameSearchInput: /Nom de l’offre/,
}

const renderIndividualOffers = async (
  filters: Partial<IndividualOffersFilters> & {
    audience?: Audience
  } = DEFAULT_SEARCH_FILTERS,
  features: string[] = [],
  user = sharedCurrentUserFactory({ id: 2 })
) => {
  const route = computeIndividualOffersUrl(filters)

  renderWithProviders(
    <Routes>
      <Route path="/offres" element={<IndividualOffers />} />
      <Route
        path="/offres/collectives"
        element={<div>Offres collectives</div>}
      />
    </Routes>,
    {
      user,
      initialRouterEntries: [route],
      features,
      storeOverrides: {
        user: {
          currentUser: user,
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )

  await userEvent.click(screen.getByRole('button', { name: /Filtrer/ }))

  await waitFor(() => {
    expect(
      within(screen.getByLabelText('Localisation')).getAllByRole('option')
        .length
    ).toBe(3)
  })
}

describe('IndividualOffers', () => {
  const scrollToContentWrapperMock = vi.fn()

  let offersRecap: ListOffersOfferResponseModel[]
  offersRecap = [listOffersOfferFactory({ venue: proVenues[0] })]

  beforeEach(() => {
    vi.spyOn(useAccessibleScrollModule, 'useAccessibleScroll').mockReturnValue({
      contentWrapperRef: { current: null },
      scrollToContentWrapper: scrollToContentWrapperMock,
    })

    vi.spyOn(apiNew, 'getCategories').mockResolvedValue(
      categoriesAndSubcategories
    )
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
      offerersNamesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
    vi.spyOn(apiNew, 'getVenueAddresses').mockResolvedValue(venueAddress)

    vi.spyOn(apiNew, 'listOffers').mockResolvedValue(offersRecap)
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  describe('filters', () => {
    it('should display only selectable categories on filters', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      await waitFor(() => {
        expect(
          screen.getByRole('option', { name: 'Cinéma' })
        ).toBeInTheDocument()
      })
      expect(screen.getByRole('option', { name: 'Jeux' })).toBeInTheDocument()
      expect(
        screen.queryByRole('option', { name: 'Technique' })
      ).not.toBeInTheDocument()
    })

    it('should filter according to page query param', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(
        Array.from({ length: 14 }, () =>
          listOffersOfferFactory({ venue: proVenues[0] })
        )
      )
      await renderIndividualOffers({ page: 2 })

      expect(
        screen.getByRole('button', { name: /Page 2 sur 2/ })
      ).toBeInTheDocument()
    })

    describe('status filters', () => {
      it('should filter on a given status filter', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        const statusSelect = screen.getByRole('combobox', {
          name: 'Statut',
        })
        await userEvent.selectOptions(statusSelect, 'Expirée')

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ status: OfferStatus.EXPIRED }),
        })
      })

      it('should indicate that no offers match selected filters', async () => {
        vi.spyOn(apiNew, 'listOffers')
          .mockResolvedValueOnce(offersRecap)
          .mockResolvedValueOnce([])

        await renderIndividualOffers()

        const statusSelect = screen.getByRole('combobox', {
          name: 'Statut',
        })
        await userEvent.selectOptions(statusSelect, 'Expirée')

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(
            screen.getByText('Aucune offre trouvée pour votre recherche')
          ).toBeInTheDocument()
        })
      })

      it('should not display column titles when no offers are returned', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce([])

        await renderIndividualOffers()

        expect(screen.queryByText('Lieu', { selector: 'th' })).toBeNull()
        expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
      })

      it('should show the "Programmée" status filter option', async () => {
        await renderIndividualOffers(DEFAULT_SEARCH_FILTERS)

        expect(
          screen.getByRole('option', { name: 'Programmée' })
        ).toBeInTheDocument()
      })
    })

    describe('on click on search button', () => {
      it('should load offers with written offer name filter', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        await userEvent.type(
          screen.getByRole('searchbox', {
            name: LABELS.nameSearchInput,
          }),
          'Any word'
        )

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ nameOrIsbn: 'Any word' }),
        })
      })

      it('should load offers with selected adress filter', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        const offererAddressOption = screen.getByLabelText('Localisation')

        const firstOffererAddressOption =
          within(offererAddressOption).getAllByRole('option')[1]

        await userEvent.selectOptions(
          offererAddressOption,
          firstOffererAddressOption
        )

        await userEvent.click(screen.getByText('Rechercher'))

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ offererAddressId: venueAddress[0].id }),
        })
      })

      it('should load offers with selected type filter', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        await waitFor(() => {
          expect(
            screen.getByRole('option', {
              name: 'Cinéma',
            })
          ).toBeInTheDocument()
        })

        const firstTypeOption = screen.getByRole('option', {
          name: 'Cinéma',
        })
        const typeSelect = screen.getByLabelText('Catégorie')
        await userEvent.selectOptions(typeSelect, firstTypeOption)

        await userEvent.click(screen.getByText('Rechercher'))

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenLastCalledWith({
            query: makeQuery({ categoryId: 'CINEMA' }),
          })
        })
      })

      it('should load offers with selected creation mode filter', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        const creationModeSelect = screen.getByRole('combobox', {
          name: 'Mode de création',
        })
        await userEvent.selectOptions(creationModeSelect, 'imported')

        await userEvent.click(screen.getByText('Rechercher'))

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ creationMode: 'imported' }),
        })
      })

      it('should load offers with selected period beginning date', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

        await userEvent.type(
          screen.getByLabelText('Début de la période'),
          '2020-12-25'
        )

        await userEvent.click(screen.getByText('Rechercher'))

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ periodBeginningDate: '2020-12-25' }),
        })
      })

      it('should load offers with selected period ending date', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        await userEvent.type(
          screen.getByLabelText('Fin de la période'),
          '2020-12-27'
        )
        await userEvent.click(screen.getByText('Rechercher'))

        await waitFor(() => {
          expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
        })
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery({ periodEndingDate: '2020-12-27' }),
        })
      })
    })
  })

  describe('url query params', () => {
    it('should have page value when page value is not first page', async () => {
      const offers = Array.from({ length: 11 }, () => listOffersOfferFactory())
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offers)

      await renderIndividualOffers()

      const nextPageIcon = screen.getByRole('button', { name: /page suivante/ })

      await userEvent.click(nextPageIcon)

      expect(
        screen.getByRole('button', { name: /Page 2 sur 2/ })
      ).toBeInTheDocument()
    })

    it('should store search value', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const searchInput = screen.getByRole('searchbox', {
        name: LABELS.nameSearchInput,
      })

      await userEvent.type(searchInput, 'search string')
      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ nameOrIsbn: 'search string' }),
      })
    })

    it('should have offer name value be removed when name search value is an empty string', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      await userEvent.clear(
        screen.getByRole('searchbox', {
          name: LABELS.nameSearchInput,
        })
      )
      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))
      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery(),
        })
      })
    })

    it('should have adress value when user filters by venue', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const offererAddressOption = screen.getByLabelText('Localisation')

      const firstOffererAddressOption =
        within(offererAddressOption).getAllByRole('option')[1]

      await userEvent.selectOptions(
        offererAddressOption,
        firstOffererAddressOption
      )
      await userEvent.click(screen.getByText('Rechercher'))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ offererAddressId: venueAddress[0].id }),
      })
    })

    it('should have venue value be removed when user asks for all venues', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)
      vi.spyOn(apiNew, 'getCategories').mockResolvedValueOnce({
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

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      await waitFor(() => {
        expect(
          screen.getByRole('option', {
            name: 'My test value',
          })
        ).toBeInTheDocument()
      })
      const firstTypeOption = screen.getByRole('option', {
        name: 'My test value',
      })
      const typeSelect = screen.getByLabelText('Catégorie')

      await userEvent.selectOptions(typeSelect, firstTypeOption)
      await userEvent.click(screen.getByText('Rechercher'))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ categoryId: 'test_id_1' }),
      })
    })

    it('should have status value when user filters by status', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce([
        listOffersOfferFactory({
          status: OfferStatus.ACTIVE,
          stocks: [],
        }),
      ])

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const statusSelect = screen.getByRole('combobox', {
        name: 'Statut',
      })
      await userEvent.selectOptions(statusSelect, 'Épuisée')

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ status: OfferStatus.SOLD_OUT }),
      })
    })

    it('should have status value be removed when user ask for all status', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce([
        listOffersOfferFactory({
          status: OfferStatus.ACTIVE,
          stocks: [],
        }),
      ])

      await renderIndividualOffers()

      const statusSelect = screen.getByRole('combobox', {
        name: 'Statut',
      })
      await userEvent.selectOptions(statusSelect, 'Tous')

      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))
      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenLastCalledWith({
          query: makeQuery(),
        })
      })
    })

    it('should have creation mode value when user filters by creation mode', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      await userEvent.selectOptions(
        screen.getByRole('combobox', { name: 'Mode de création' }),
        'manual'
      )
      await userEvent.click(screen.getByText('Rechercher'))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ creationMode: 'manual' }),
      })
    })

    it('should have creation mode value be removed when user ask for all creation modes', async () => {
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

      await renderIndividualOffers()

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const searchButton = screen.getByText('Rechercher')
      await userEvent.selectOptions(
        screen.getByRole('combobox', { name: 'Mode de création' }),
        'manual'
      )
      await userEvent.click(searchButton)

      await userEvent.selectOptions(
        await screen.findByDisplayValue('Manuel'),
        'Tous'
      )
      await userEvent.click(searchButton)

      expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ creationMode: 'manual' }),
      })
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () => listOffersOfferFactory())
      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offers)
      await renderIndividualOffers()
      const nextIcon = screen.getByRole('button', { name: /page suivante/ })

      await userEvent.click(nextIcon)

      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByLabelText(offers[0].name)).not.toBeInTheDocument()
      expect(scrollToContentWrapperMock).toHaveBeenCalledTimes(1)
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () => listOffersOfferFactory())

      vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offers)
      await renderIndividualOffers()
      const nextIcon = screen.getByRole('button', { name: /page suivante/ })
      await userEvent.click(nextIcon)
      const previousIcon = screen.getByRole('button', {
        name: /page précédente/,
      })

      await userEvent.click(previousIcon)

      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
      expect(scrollToContentWrapperMock).toHaveBeenCalledTimes(2)
    })

    describe('when 101 offers are fetched', () => {
      beforeEach(() => {
        offersRecap = Array.from({ length: 101 }, () =>
          listOffersOfferFactory({ stocks: [] })
        )
      })

      it('should have max number page of 10', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)

        await renderIndividualOffers()

        expect(
          screen.getByRole('button', { name: /Page 1 sur 10/ })
        ).toBeInTheDocument()
      })

      it('should not display the 101st offer', async () => {
        vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)
        await renderIndividualOffers()
        const nextIcon = screen.getByRole('button', { name: /page suivante/ })

        for (let i = 1; i < 11; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[99].name)).toBeInTheDocument()
        expect(
          screen.queryByLabelText(offersRecap[100].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('should reset filters', () => {
    it('when clicking on "afficher toutes les offres" when no offers are displayed', async () => {
      vi.spyOn(apiNew, 'listOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce([])

      await renderIndividualOffers({ categoryId: 'CINEMA' })

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const offererAddressOption = screen.getByLabelText('Localisation')

      await waitFor(() => {
        expect(within(offererAddressOption).getAllByRole('option').length).toBe(
          3
        )
      })

      const firstOffererAddressOption =
        within(offererAddressOption).getAllByRole('option')[1]

      await userEvent.selectOptions(
        offererAddressOption,
        firstOffererAddressOption
      )
      await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({
          categoryId: 'CINEMA',
          offererAddressId: venueAddress[0].id,
        }),
      })

      screen.getByText(/Aucune offre trouvée pour votre recherche/)

      await userEvent.click(screen.getByText(/Afficher toutes les offres/))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(3)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({ query: makeQuery() })
    })

    it('when clicking on "Réinitialiser les filtres" - except nameOrIsbn', async () => {
      vi.spyOn(apiNew, 'listOffers')
        .mockResolvedValueOnce(offersRecap)
        .mockResolvedValueOnce([])

      const nameOrIsbn = 'Any word'

      await renderIndividualOffers({ nameOrIsbn, categoryId: 'CINEMA' })

      expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

      const offererAddressOption = screen.getByLabelText('Localisation')

      await waitFor(() => {
        expect(within(offererAddressOption).getAllByRole('option').length).toBe(
          3
        )
      })

      const firstOffererAddressOption =
        within(offererAddressOption).getAllByRole('option')[1]

      await userEvent.selectOptions(
        offererAddressOption,
        firstOffererAddressOption
      )
      await userEvent.click(screen.getByRole('button', { name: /Rechercher/ }))

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({
          nameOrIsbn,
          categoryId: 'CINEMA',
          offererAddressId: venueAddress[0].id,
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser les filtres/ })
      )

      await waitFor(() => {
        expect(apiNew.listOffers).toHaveBeenCalledTimes(3)
      })
      expect(apiNew.listOffers).toHaveBeenLastCalledWith({
        query: makeQuery({ nameOrIsbn }),
      })
    })
  })
  it('should have offerer address value when user filters by address', async () => {
    vi.spyOn(apiNew, 'listOffers').mockResolvedValueOnce(offersRecap)
    vi.spyOn(api, 'getVenueAddresses').mockResolvedValueOnce(venueAddress)
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(
      defaultGetOffererResponseModel
    )
    await renderIndividualOffers(DEFAULT_SEARCH_FILTERS)

    expect(apiNew.listOffers).toHaveBeenCalledTimes(1)

    const venueAddressOption = screen.getByLabelText('Localisation')

    await waitFor(() => {
      expect(within(venueAddressOption).getAllByRole('option').length).toBe(3)
    })

    const firstOffererAddressOption =
      within(venueAddressOption).getAllByRole('option')[1]

    await userEvent.selectOptions(venueAddressOption, firstOffererAddressOption)
    await userEvent.click(screen.getByText('Rechercher'))

    await waitFor(() => {
      expect(apiNew.listOffers).toHaveBeenCalledTimes(2)
    })
    expect(apiNew.listOffers).toHaveBeenLastCalledWith({
      query: makeQuery({
        offererAddressId: venueAddress[0].id,
      }),
    })
  })
})
