import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  type CollectiveOffersStockResponseModel,
  CollectiveOfferType,
} from '@/apiClient/v1'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { TemplateCollectiveOffers } from '../TemplateCollectiveOffers'

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
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  features: string[] = []
) => {
  const route = computeCollectiveOffersUrl(filters)

  const user = sharedCurrentUserFactory()
  renderWithProviders(<TemplateCollectiveOffers />, {
    user,
    initialRouterEntries: [route],
    features,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const stocks: Array<CollectiveOffersStockResponseModel> = [
  {
    startDatetime: String(new Date()),
    hasBookingLimitDatetimePassed: false,
    remainingQuantity: 1,
  },
]
const offersRecap: CollectiveOfferResponseModel[] = [
  collectiveOfferFactory({ stocks }),
]

describe('TemplateCollectiveOffers', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      name: 'Mon offerer',
    })
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  it('should display the page', async () => {
    await renderOffers()

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalledWith(1)
    })
    expect(screen.getByText('Offres vitrines')).toBeInTheDocument()
  })

  describe('filters', () => {
    describe('status filters', () => {
      it('should filter offers given status filter when clicking on "Appliquer"', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)
        await renderOffers()

        await userEvent.click(
          screen.getByRole('button', {
            name: 'Statut',
          })
        )

        await userEvent.click(screen.getByText('Non conforme'))

        await userEvent.click(
          screen.getByRole('button', { name: 'Rechercher' })
        )

        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenNthCalledWith(
            2,
            undefined,
            '1',
            [CollectiveOfferDisplayedStatus.REJECTED],
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.TEMPLATE,
            undefined
          )
        })
      })

      it('should not display column titles when no offers are returned', async () => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([])

        await renderOffers()

        expect(screen.queryByText('Stock', { selector: 'th' })).toBeNull()
      })
    })

    describe('on click on search button', () => {
      it('should load offers with written offer name filter', async () => {
        await renderOffers()

        await userEvent.type(
          screen.getByRole('searchbox', {
            name: 'Nom de l’offre',
          }),
          'Any word'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenCalledWith(
            'Any word',
            '1',
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            CollectiveOfferType.TEMPLATE,
            undefined
          )
        })
      })

      it('should load offers with selected period beginning date', async () => {
        await renderOffers()

        await userEvent.type(
          screen.getByLabelText('Début de la période'),
          '2020-12-25'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            '1',
            undefined,
            undefined,
            undefined,
            '2020-12-25',
            undefined,
            CollectiveOfferType.TEMPLATE,
            undefined
          )
        })
      })

      it('should load offers with selected period ending date', async () => {
        await renderOffers()
        await userEvent.type(
          screen.getByLabelText('Fin de la période'),
          '2020-12-27'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
            undefined,
            '1',
            undefined,
            undefined,
            undefined,
            undefined,
            '2020-12-27',
            CollectiveOfferType.TEMPLATE,
            undefined
          )
        })
      })
    })
  })

  describe('page navigation', () => {
    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stocks })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

      await userEvent.click(nextIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferFactory({ stocks })
      )
      vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offers)
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: 'Page suivante' })
      const previousIcon = screen.getByRole('button', {
        name: 'Page précédente',
      })
      await userEvent.click(nextIcon)

      await userEvent.click(previousIcon)

      expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 101 offers are fetched', () => {
      const offersRecap = Array.from({ length: 101 }, () =>
        collectiveOfferFactory({ stocks })
      )

      beforeEach(() => {
        vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offersRecap)
      })

      it('should have max number page of 10', async () => {
        await renderOffers()

        expect(screen.getByText('Page 1/10')).toBeInTheDocument()
      })

      it('should not display the 101st offer', async () => {
        await renderOffers()
        const nextIcon = screen.getByRole('button', { name: 'Page suivante' })

        for (let i = 1; i < 11; i++) {
          await userEvent.click(nextIcon)
        }

        expect(screen.getByLabelText(offersRecap[99].name)).toBeInTheDocument()
        expect(
          screen.queryByText(offersRecap[100].name)
        ).not.toBeInTheDocument()
      })
    })
  })

  it('should show draft offers', async () => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce([
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }),
      collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      }),
    ])
    await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)

    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })
})
