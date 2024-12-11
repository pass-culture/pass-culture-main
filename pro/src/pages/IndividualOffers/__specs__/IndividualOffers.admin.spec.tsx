import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  ALL_VENUES,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { computeIndividualOffersUrl } from 'commons/core/Offers/utils/computeIndividualOffersUrl'
import { Audience } from 'commons/core/shared/types'
import {
  listOffersOfferFactory,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { IndividualOffers } from '../IndividualOffers'

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
  } = DEFAULT_SEARCH_FILTERS,
  user = sharedCurrentUserFactory({ isAdmin: true }),
  selectedOffererId: number | null = 1
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
      storeOverrides: {
        user: {
          currentUser: user,
          selectedOffererId,
        },
      },
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
      '1',
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
