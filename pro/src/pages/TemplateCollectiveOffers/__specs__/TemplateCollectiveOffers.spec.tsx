import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api, apiNew } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferTemplateResponseModel,
  type GetVenueAddressResponseModel,
  type ListCollectiveOffersQueryModel,
} from '@/apiClient/v1/new'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { collectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  venueAddressFactory,
} from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { TemplateCollectiveOffers } from '../TemplateCollectiveOffers'

const venueAddress: GetVenueAddressResponseModel[] = [
  venueAddressFactory(1, {
    city: 'London',
  }),
  venueAddressFactory(1, {
    city: 'New York',
  }),
]

const renderOffers = async (
  filters: Partial<CollectiveSearchFiltersParams> = DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  features: string[] = []
) => {
  const route = computeCollectiveOffersUrl(
    filters,
    DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    true
  )

  const user = sharedCurrentUserFactory()
  renderWithProviders(<TemplateCollectiveOffers />, {
    user,
    initialRouterEntries: [route],
    features,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
      },
    },
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const makeQuery = (
  overrides: Partial<ListCollectiveOffersQueryModel> = {}
): ListCollectiveOffersQueryModel => ({
  format: null,
  locationType: null,
  name: null,
  offererAddressId: null,
  offererId: null,
  periodBeginningDate: null,
  periodEndingDate: null,
  status: null,
  venueId: 2,
  ...overrides,
})

const offersRecap: CollectiveOfferTemplateResponseModel[] = [
  collectiveOfferTemplateFactory(),
]

describe('TemplateCollectiveOffers', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValue(
      offersRecap
    )
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
      offerersNamesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      name: 'Mon offerer',
    })
    vi.spyOn(apiNew, 'getVenueAddresses').mockResolvedValue(venueAddress)
  })

  afterEach(() => {
    window.sessionStorage.clear()
  })

  it('should display the page', async () => {
    await renderOffers()

    expect(
      screen.getByText('Offres vitrines', {
        selector: 'h1',
      })
    ).toBeInTheDocument()
  })

  describe('filters', () => {
    describe('status filters', () => {
      it('should filter offers given status filter when clicking on "Appliquer"', async () => {
        vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
          offersRecap
        )
        await renderOffers()

        await userEvent.click(screen.getByRole('button', { name: /Filtrer/ }))

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
          expect(apiNew.getCollectiveOfferTemplates).toHaveBeenNthCalledWith(
            2,
            {
              query: makeQuery({
                status: [CollectiveOfferDisplayedStatus.REJECTED],
              }),
            }
          )
        })
      })

      it('should not display column titles when no offers are returned', async () => {
        vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce([])

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
          expect(apiNew.getCollectiveOfferTemplates).toHaveBeenCalledWith({
            query: makeQuery({ name: 'Any word' }),
          })
        })
      })

      it('should load offers with selected period beginning date', async () => {
        await renderOffers()

        await userEvent.click(screen.getByRole('button', { name: /Filtrer/ }))

        await userEvent.type(
          screen.getByLabelText('Début de la période'),
          '2020-12-25'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(apiNew.getCollectiveOfferTemplates).toHaveBeenLastCalledWith({
            query: makeQuery({ periodBeginningDate: '2020-12-25' }),
          })
        })
      })

      it('should load offers with selected period ending date', async () => {
        await renderOffers()

        await userEvent.click(screen.getByRole('button', { name: /Filtrer/ }))

        await userEvent.type(
          screen.getByLabelText('Fin de la période'),
          '2020-12-27'
        )

        await userEvent.click(screen.getByText('Rechercher'))
        await waitFor(() => {
          expect(apiNew.getCollectiveOfferTemplates).toHaveBeenLastCalledWith({
            query: makeQuery({ periodEndingDate: '2020-12-27' }),
          })
        })
      })
    })
  })

  describe('page navigation', () => {
    // Necessary because JSDOM doesn't implement the `scrollTo` method
    // (which is used by the `useAccessibleScroll` hook in that component's scope)
    beforeAll(() => {
      Element.prototype.scrollTo = () => {}
      window.scrollTo = () => {}
    })

    it('should display next page when clicking on right arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferTemplateFactory()
      )
      vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offers
      )
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: /page suivante/ })

      await userEvent.click(nextIcon)

      expect(apiNew.getCollectiveOfferTemplates).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[10].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[0].name)).not.toBeInTheDocument()
    })

    it('should display previous page when clicking on left arrow', async () => {
      const offers = Array.from({ length: 11 }, () =>
        collectiveOfferTemplateFactory()
      )
      vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
        offers
      )
      await renderOffers()
      const nextIcon = screen.getByRole('button', { name: /page suivante/ })
      const previousIcon = screen.getByRole('button', {
        name: 'Page précédente',
      })
      await userEvent.click(nextIcon)

      await userEvent.click(previousIcon)

      expect(apiNew.getCollectiveOfferTemplates).toHaveBeenCalledTimes(1)
      expect(screen.getByLabelText(offers[0].name)).toBeInTheDocument()
      expect(screen.queryByText(offers[10].name)).not.toBeInTheDocument()
    })

    describe('when 101 offers are fetched', () => {
      const offersRecap = Array.from({ length: 101 }, () =>
        collectiveOfferTemplateFactory()
      )

      beforeEach(() => {
        vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValue(
          offersRecap
        )
      })

      it('should have max number page of 10', async () => {
        await renderOffers()

        expect(
          screen.getByRole('button', { name: /Page 1 sur 10/ })
        ).toBeInTheDocument()
      })

      it('should not display the 101st offer', async () => {
        await renderOffers()
        const nextIcon = screen.getByRole('button', { name: /page suivante/ })

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
    vi.spyOn(apiNew, 'getCollectiveOfferTemplates').mockResolvedValueOnce([
      collectiveOfferTemplateFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }),
      collectiveOfferTemplateFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      }),
    ])
    await renderOffers(DEFAULT_COLLECTIVE_SEARCH_FILTERS)

    expect(screen.getByText('2 offres')).toBeInTheDocument()
  })
})
