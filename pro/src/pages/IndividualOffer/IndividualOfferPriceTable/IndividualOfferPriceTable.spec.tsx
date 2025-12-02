import { screen, waitFor } from '@testing-library/react'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

vi.mock('@/apiClient/api', () => ({
  api: { getStocks: vi.fn() },
}))

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { IndividualOfferPriceTable } from './IndividualOfferPriceTable'

const LABELS = {
  headings: {
    priceTable: 'Tarifs',
  },
  texts: {
    loading: 'Chargement en cours',
  },
}

const renderIndividualOfferPriceTable: RenderComponentFunction<
  void,
  IndividualOfferContextValues,
  {
    offer: GetIndividualOfferWithAddressResponseModel | null
    offerId?: number
  }
> = (params) => {
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: params.offer?.isEvent ?? null,
    offer: params.offer,
    offerId: params.offer?.id ?? params.offerId ?? null,
    setIsEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferPriceTable />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<IndividualOfferSummaryPriceTable />', () => {
  it('should show spinner when offer is fetching', () => {
    renderIndividualOfferPriceTable({
      offer: null,
      offerId: 1,
    })

    expect(screen.getByText(LABELS.texts.loading)).toBeInTheDocument()
  })

  it('should render layout, screen and action bar when stocks loaded', async () => {
    vi.spyOn(api, 'getStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [getOfferStockFactory({ id: 2 })],
      })
    )

    const offer = getIndividualOfferFactory({
      id: 1,
      hasStocks: true,
      isEvent: false,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
    })

    renderIndividualOfferPriceTable({ offer })

    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: LABELS.headings.priceTable })
      ).toBeInTheDocument()
    )
    expect(api.getStocks).toHaveBeenCalledWith(offer.id)
  })

  it('should not call stocks for an event offer', async () => {
    vi.spyOn(api, 'getStocks').mockResolvedValueOnce(
      getStocksResponseFactory({
        stocks: [getOfferStockFactory({ id: 2 })],
      })
    )

    const offer = getIndividualOfferFactory({
      id: 1,
      hasStocks: true,
      isEvent: true,
      subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
    })

    renderIndividualOfferPriceTable({ offer })

    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: LABELS.headings.priceTable })
      ).toBeInTheDocument()
    )

    expect(api.getStocks).not.toHaveBeenCalled()
  })
})
