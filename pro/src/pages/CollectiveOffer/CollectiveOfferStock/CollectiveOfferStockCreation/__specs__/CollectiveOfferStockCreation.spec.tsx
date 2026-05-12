import { screen, waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { MandatoryCollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferStockCreation } from '../CollectiveOfferStockCreation'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
  },
}))

const renderCollectiveStockCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
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

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferStockCreation', () => {
  it('should render collective offer stock form', async () => {
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', defaultProps)

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
    const props = {
      ...defaultProps,
      offer: { ...defaultProps.offer, templateId: 12 },
    }
    const offerTemplate = getCollectiveOfferTemplateFactory({
      educationalPriceDetail: 'Details from template',
    })
    vi.spyOn(apiNew, 'getCollectiveOfferTemplate').mockResolvedValue(
      offerTemplate
    )
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', props)
    await waitFor(() => {
      expect(apiNew.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    })
  })

  it('should render collective offer stock form from requested offer', async () => {
    const offerTemplate = getCollectiveOfferTemplateFactory({
      educationalPriceDetail: 'Details from template',
    })
    vi.spyOn(apiNew, 'getCollectiveOfferTemplate').mockResolvedValue(
      offerTemplate
    )
    renderCollectiveStockCreation(
      '/offre/A1/collectif/stocks?requete=1',
      defaultProps
    )
    await waitFor(() => {
      expect(apiNew.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)
    })
  })
})
