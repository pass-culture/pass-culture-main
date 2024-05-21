import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { ALL_VENUES, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { Audience } from 'core/shared/types'
import {
  defaultGetOffererResponseModel,
  listOffersOfferFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

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
  venueListItemFactory({
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    publicName: undefined,
    isVirtual: false,
  }),
  venueListItemFactory({
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  }),
]

const renderOffers = async (
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
      user: sharedCurrentUserFactory({ isAdmin: true }),
      initialRouterEntries: [route],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('route Offers when user is admin', () => {
  let offersRecap: ListOffersOfferResponseModel[]

  beforeEach(() => {
    offersRecap = [listOffersOfferFactory({ venue: proVenues[0] })]
    vi.spyOn(api, 'listOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce(
      categoriesAndSubcategories
    )
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
  })

  // status filter can only be used with an offerer or a venue filter for performance reasons
  it('should reset and disable status filter when venue filter is deselected', async () => {
    const { id: venueId, name: venueName } = proVenues[0]
    const filters = {
      venueId: venueId.toString(),
      status: OfferStatus.INACTIVE,
    }
    await renderOffers(filters)

    await userEvent.selectOptions(
      screen.getByDisplayValue(venueName),
      ALL_VENUES
    )

    await userEvent.click(screen.getByText('Rechercher'))

    await waitFor(() => {
      expect(api.listOffers).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        OfferStatus.INACTIVE,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })
    expect(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    ).toBeDisabled()
  })

  it('should not reset or disable status filter when venue filter is deselected while offerer filter is applied', async () => {
    const { id: venueId, name: venueName } = proVenues[0]
    const filters = {
      venueId: venueId.toString(),
      status: OfferStatus.INACTIVE,
      offererId: 'EF',
    }
    await renderOffers(filters)
    await userEvent.selectOptions(
      screen.getByDisplayValue(venueName),
      ALL_VENUES
    )

    await userEvent.click(screen.getByText('Rechercher'))

    await waitFor(() => {
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
    expect(
      screen.getByRole('button', {
        name: /Afficher ou masquer le filtre par statut/,
      })
    ).not.toBeDisabled()
  })

  it('should reset and disable status filter when offerer filter is removed', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    const filters = {
      offererId: defaultGetOffererResponseModel.id.toString(),
      status: OfferStatus.INACTIVE,
    }
    await renderOffers(filters)

    await userEvent.click(screen.getByTestId('remove-offerer-filter'))

    await waitFor(() => {
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

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    ).toBeDisabled()
  })

  it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
    const { id: venueId } = proVenues[0]

    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    const filters = {
      venueId: venueId.toString(),
      status: OfferStatus.INACTIVE,
      offererId: defaultGetOffererResponseModel.id.toString(),
    }
    await renderOffers(filters)

    await userEvent.click(screen.getByTestId('remove-offerer-filter'))
    await waitFor(() => {
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

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByRole('button', {
        name: /Afficher ou masquer le filtre par statut/,
      })
    ).not.toBeDisabled()
  })

  it('should enable status filters when venue filter is applied', async () => {
    const filters = { venueId: 'IJ' }

    await renderOffers(filters)

    expect(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    ).not.toBeDisabled()
  })

  it('should enable status filters when offerer filter is applied', async () => {
    const filters = { offererId: 'A4' }

    await renderOffers(filters)

    expect(
      screen.getByRole('button', {
        name: 'Statut Afficher ou masquer le filtre par statut',
      })
    ).not.toBeDisabled()
  })
})
