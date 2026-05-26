import { screen, waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import {
  defaultGetCollectiveOfferRequest,
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
  },
}))

vi.mock('../../components/OfferEducationalStock/OfferEducationalStock', () => ({
  OfferEducationalStock: vi.fn(() => <div data-testid="stock-form" />),
}))

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

afterEach(() => {
  vi.clearAllMocks()
})

describe('CollectiveOfferStockCreation', () => {
  it('should render collective offer stock form', async () => {
    vi.mocked(OfferEducationalStock).mockImplementation(
      await vi
        .importActual<
          typeof import('../../components/OfferEducationalStock/OfferEducationalStock')
        >('../../components/OfferEducationalStock/OfferEducationalStock')
        .then((m) => m.OfferEducationalStock)
    )

    renderCollectiveStockCreation('/offre/A1/collectif/stocks', {
      offer: getCollectiveOfferFactory(),
    })

    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Indiquez le prix et la date de votre offre',
      })
    ).toBeInTheDocument()
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
})
