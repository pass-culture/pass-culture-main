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

  // As an admin, the status filter can only be used with an offerer or a venue filter for performance reasons
  it('should reset status filter when venue filter is deselected', async () => {
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
  })

  it('should reset status filter when offerer filter is removed', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    const filters = {
      offererId: defaultGetOffererResponseModel.id.toString(),
      status: OfferStatus.INACTIVE,
    }
    await renderOffers(filters)

    await userEvent.click(screen.getByTestId('remove-offerer-filter'))

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

  it('should not reset status filter when offerer filter is removed while venue filter is applied', async () => {
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
})
