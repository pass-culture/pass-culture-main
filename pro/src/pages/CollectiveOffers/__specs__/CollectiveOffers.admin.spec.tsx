import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveOfferResponseModel,
  CollectiveOffersStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ALL_VENUES, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

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
  filters: Partial<SearchFiltersParams> = DEFAULT_SEARCH_FILTERS
) => {
  const route = computeCollectiveOffersUrl(filters)

  renderWithProviders(<CollectiveOffers />, {
    user: sharedCurrentUserFactory({ isAdmin: true }),
    initialRouterEntries: [route],
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

describe('route CollectiveOffers when user is admin', () => {
  let offersRecap: CollectiveOfferResponseModel[]
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      beginningDatetime: String(new Date()),
      hasBookingLimitDatetimePassed: false,
      remainingQuantity: 1,
    },
  ]

  beforeEach(() => {
    offersRecap = [collectiveOfferFactory({ stocks })]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
  })

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

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
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
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        'EF',
        'INACTIVE',
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })
    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).not.toBeDisabled()
  })

  it('should reset and disable status filter for performance reasons when offerer filter is removed', async () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      name: 'La structure',
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    const filters = {
      offererId: String(offerer.id),
      status: OfferStatus.INACTIVE,
    }
    await renderOffers(filters)

    await userEvent.click(screen.getByTestId('remove-offerer-filter'))

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
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
    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).toBeDisabled()
  })

  it('should not reset or disable status filter when offerer filter is removed while venue filter is applied', async () => {
    const { id: venueId } = proVenues[0]
    const offerer = {
      ...defaultGetOffererResponseModel,
      name: 'La structure',
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    const filters = {
      venueId: venueId.toString(),
      status: OfferStatus.INACTIVE,
      offererId: String(offerer.id),
    }
    await renderOffers(filters)

    await userEvent.click(screen.getByTestId('remove-offerer-filter'))

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        'INACTIVE',
        venueId.toString(),
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined
      )
    })
    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).not.toBeDisabled()
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

  it('should enable status filters when offerer filter is applied', async () => {
    const filters = { offererId: 'A4' }

    await renderOffers(filters)

    expect(
      screen.getByRole('combobox', {
        name: 'Statut',
      })
    ).not.toBeDisabled()
  })
})
