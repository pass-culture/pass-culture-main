import { screen, waitFor } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient//api'
import {
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient//v1'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveOfferSummaryEdition } from './CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@/apiClient//api', () => ({
  api: {
    listEducationalOfferers: vi.fn(),
  },
}))

const renderCollectiveOfferSummaryEdition = (
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferSummaryEdition offer={offer} />, {
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('CollectiveOfferSummary', () => {
  let offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel

  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })

  beforeEach(() => {
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [offerer],
    })
  })

  it('should display hide offer option when action is allowed', async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
      isActive: true,
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
    })

    renderCollectiveOfferSummaryEdition(offer)

    const desactivateOffer = await screen.findByRole('button', {
      name: 'Mettre en pause',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })
  it('should display new component for new collective offer detail page when offer is bookable and FF is enabled', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferFactory(), {
      features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE'],
    })

    expect(await screen.findByText('n°2')).toBeInTheDocument()
  })

  it('should not display new component for new collective offer detail page when offer is template and FF is enabled', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferTemplateFactory(), {
      features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE'],
    })

    await waitFor(() =>
      expect(screen.queryByText('n°2')).not.toBeInTheDocument()
    )
  })
})
