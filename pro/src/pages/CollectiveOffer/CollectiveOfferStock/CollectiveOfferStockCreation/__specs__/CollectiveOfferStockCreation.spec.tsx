import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import type { CollectiveStockCreationBodyModel } from '@/apiClient/v1/new'
import {
  defaultGetCollectiveOfferRequest,
  getCollectiveOfferCollectiveStockFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { CollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { OfferEducationalStock } from '../../components/OfferEducationalStock/OfferEducationalStock'
import { CollectiveOfferStockCreation } from '../CollectiveOfferStockCreation'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    editCollectiveStock: vi.fn(),
    createCollectiveStock: vi.fn(),
  },
}))

vi.mock('../../components/OfferEducationalStock/OfferEducationalStock', () => ({
  OfferEducationalStock: vi.fn(() => <div data-testid="stock-form" />),
}))

const setSubmitResponse = (
  newCollectiveStock: Partial<CollectiveStockCreationBodyModel>
) => {
  vi.mocked(OfferEducationalStock).mockImplementationOnce(
    vi.fn(({ onSubmit }) => {
      return (
        <button onClick={() => onSubmit(newCollectiveStock)}>
          Enregistrer
        </button>
      )
    })
  )
}

const renderCollectiveStockCreation = (
  path: string,
  props: CollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferStockCreation {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          allowedOnAdage: true,
        }),
      },
    },
  })
}

describe('CollectiveOfferStockCreation', () => {
  it('should render collective offer stock form', async () => {
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', {
      offer: getCollectiveOfferFactory(),
    })

    expect(await screen.findByTestId('stock-form')).toBeInTheDocument()
  })

  it('should render collective offer stock form from template', async () => {
    vi.spyOn(apiNew, 'getCollectiveOfferTemplate').mockResolvedValue(
      getCollectiveOfferTemplateFactory({
        educationalPriceDetail: 'Details from template',
      })
    )
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', {
      offer: getCollectiveOfferFactory({
        collectiveStock: null,
        templateId: 12,
      }),
    })
    await waitFor(() => {
      expect(apiNew.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    })
    expect(OfferEducationalStock).toHaveBeenCalledTimes(2) // first render before api request resolves
    expect(OfferEducationalStock).toHaveBeenLastCalledWith(
      expect.objectContaining({
        initialStock: { educationalPriceDetail: 'Details from template' },
      }),
      undefined
    )
  })

  it('should render collective offer stock form from requested offer', async () => {
    renderCollectiveStockCreation('/offre/A1/collectif/stocks?requete=1', {
      offer: getCollectiveOfferFactory(),
    })
    await waitFor(() => {
      expect(apiNew.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)
    })
  })

  it.each([
    {
      partialRequest: {
        requestedDate: '2030-07-30',
        totalStudents: 10,
        totalTeachers: 5,
      },
      expectedStock: { numberOfTickets: 15, startDatetime: '2030-07-30' },
    },
    {
      partialRequest: {
        requestedDate: null,
        totalStudents: null,
        totalTeachers: null,
      },
      expectedStock: {},
    },
    {
      partialRequest: { totalStudents: 10 },
      expectedStock: { numberOfTickets: 10 },
    },
    {
      partialRequest: { totalTeachers: 5 },
      expectedStock: { numberOfTickets: 5 },
    },
  ])('should initialize stock with $expectedStock when a requested offer has $partialRequest', async ({
    partialRequest,
    expectedStock,
  }) => {
    vi.spyOn(apiNew, 'getCollectiveOfferRequest').mockResolvedValue({
      ...defaultGetCollectiveOfferRequest,
      ...partialRequest,
    })

    renderCollectiveStockCreation('/offre/A1/collectif/stocks?requete=1', {
      offer: getCollectiveOfferFactory({ collectiveStock: null }),
    })
    await waitFor(() => {
      expect(apiNew.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)
    })
    expect(OfferEducationalStock).toHaveBeenCalledTimes(2) // first render before api request resolves
    expect(OfferEducationalStock).toHaveBeenLastCalledWith(
      expect.objectContaining({
        initialStock: expectedStock,
      }),
      undefined
    )
  })

  it('on submit : should call creation endpoint if no stock exists yet on offer', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory({ collectiveStock: null })
    const collectiveStock: Record<string, any> =
      getCollectiveOfferCollectiveStockFactory()
    delete collectiveStock.id
    // TODO (mdesquilbet, 2026-05-29): clean when totalPrice will be renamed
    collectiveStock.totalPrice = collectiveStock.price
    delete collectiveStock.price
    setSubmitResponse(collectiveStock)
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', { offer })

    expect(apiNew.createCollectiveStock).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(apiNew.editCollectiveStock).not.toHaveBeenCalled()
    expect(apiNew.createCollectiveStock).toHaveBeenCalledExactlyOnceWith({
      body: {
        ...collectiveStock,
        offerId: offer.id,
      },
    })
  })

  it('on submit : should call edition endpoint if a stock already exists on the offer', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    setSubmitResponse({ numberOfTickets: 12 })
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', { offer })

    expect(apiNew.editCollectiveStock).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(apiNew.createCollectiveStock).not.toHaveBeenCalled()
    expect(apiNew.editCollectiveStock).toHaveBeenCalledExactlyOnceWith({
      path: { collective_stock_id: offer.collectiveStock?.id },
      body: { numberOfTickets: 12 },
    })
  })

  it('on submit : should raise an error if no stock exists yet on offer and called with partial stock', async () => {
    const user = userEvent.setup()
    vi.spyOn(console, 'error').mockImplementationOnce(() => {})

    const offer = getCollectiveOfferFactory({ collectiveStock: null })
    setSubmitResponse({ numberOfTickets: 12 })
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', { offer })

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(console.error).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Missing required values',
      })
    )
    expect(apiNew.createCollectiveStock).not.toHaveBeenCalled()
    expect(apiNew.editCollectiveStock).not.toHaveBeenCalled()
  })
})
