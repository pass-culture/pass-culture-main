import { screen } from '@testing-library/react'
import { vi } from 'vitest'

import {
  type GetIndividualOfferWithAddressResponseModel,
  type GetOfferStockResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { IndividualOfferSummaryPriceTableScreen } from './IndividualOfferSummaryPriceTableScreen'

const LABELS = {
  headings: {
    tariffs: 'Tarifs',
  },
  texts: {
    quantity: 'Quantité',
    noStocks: 'Vous n’avez aucun stock renseigné.',
  },
}

const renderIndividualOfferSummaryPriceTableScreen: RenderComponentFunction<
  React.ComponentProps<typeof IndividualOfferSummaryPriceTableScreen>,
  IndividualOfferContextValues,
  {
    offer: GetIndividualOfferWithAddressResponseModel
    offerStocks: GetOfferStockResponseModel[]
  }
> = (params) => {
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    subCategories: MOCKED_SUBCATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: params.offer.isEvent,
    offer: params.offer,
    offerId: params.offer.id,
    setIsEvent: vi.fn(),
    ...params.contextValues,
  }
  const props = {
    offer: params.offer,
    offerStocks: params.offerStocks,
    ...params.props,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferSummaryPriceTableScreen {...props} />
    </IndividualOfferContext.Provider>
  )
}

describe('<IndividualOfferSummaryPriceTableScreen />', () => {
  it('should render PriceCategoriesSection for event offers', () => {
    const offer = getIndividualOfferFactory({
      id: 1,
      isEvent: true,
      subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
    })
    const offerStocks = [getOfferStockFactory({ id: 2 })]

    renderIndividualOfferSummaryPriceTableScreen({
      offer,
      offerStocks,
    })

    expect(
      screen.getByRole('heading', { name: LABELS.headings.tariffs })
    ).toBeInTheDocument()
    expect(screen.queryByText(LABELS.texts.quantity)).not.toBeInTheDocument()
  })

  it('should render stock section without warning when active offer has stocks', () => {
    const offer = getIndividualOfferFactory({
      id: 1,
      hasStocks: true,
      isEvent: false,
      status: OfferStatus.ACTIVE,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
    })
    const offerStocks = [getOfferStockFactory({ id: 2 })]

    renderIndividualOfferSummaryPriceTableScreen({
      offer,
      offerStocks,
    })

    expect(
      screen.getByRole('heading', { name: LABELS.headings.tariffs })
    ).toBeInTheDocument()
    expect(screen.queryByText(LABELS.texts.noStocks)).not.toBeInTheDocument()
    expect(screen.getByText(/Quantité/)).toBeInTheDocument()
  })

  it('should render warning when offer has no stocks', () => {
    const offer = getIndividualOfferFactory({
      isEvent: false,
      hasStocks: false,
      status: OfferStatus.SOLD_OUT,
      subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
    })
    const offerStocks: GetOfferStockResponseModel[] = []

    renderIndividualOfferSummaryPriceTableScreen({
      offer,
      offerStocks,
    })

    expect(screen.getByText(LABELS.texts.noStocks)).toBeInTheDocument()
  })
})
