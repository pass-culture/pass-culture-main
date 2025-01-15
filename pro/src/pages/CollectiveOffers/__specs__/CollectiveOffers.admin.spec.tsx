import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOffersStockResponseModel,
} from 'apiClient/v1'
import {
  ALL_VENUES,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOffers } from '../CollectiveOffers'

const proVenues = [
  venueListItemFactory({
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
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
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)
  const user = sharedCurrentUserFactory({ isAdmin: true })

  renderWithProviders(<CollectiveOffers />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { selectedOffererId: 1, offererNames: [] },
    },
    initialRouterEntries: [route],
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('route CollectiveOffers when user is admin', () => {
  let offersRecap: CollectiveOfferResponseModel[]
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      startDatetime: String(new Date()),
      hasBookingLimitDatetimePassed: false,
      remainingQuantity: 1,
    },
  ]

  beforeEach(() => {
    offersRecap = [collectiveOfferFactory({ stocks })]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
    const offerer = {
      ...defaultGetOffererResponseModel,
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
  })

  it('should reset status filter when venue filter is deselected', async () => {
    const { id: venueId, name: venueName } = proVenues[0]
    const filters = {
      venueId: venueId.toString(),
      status: [CollectiveOfferDisplayedStatus.INACTIVE],
    }
    const offerer = {
      ...defaultGetOffererResponseModel,
      name: venueName,
      id: venueId,
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    await renderOffers(filters)
    await waitFor(() => {
      expect(api.getVenues).toHaveBeenCalledWith(null, null, 1)
    })
    await userEvent.selectOptions(
      screen.getByDisplayValue(venueName),
      ALL_VENUES
    )

    await userEvent.click(screen.getByText('Rechercher'))

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        '1',
        [],
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

  it('should enable status filters when venue filter is applied', async () => {
    const filters = { venueId: proVenues[0].id.toString() }

    await renderOffers(filters)

    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).not.toBeDisabled()
  })
})
