import { screen, waitFor } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
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
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveOfferSummaryEdition } from './CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('@/apiClient/api', () => ({
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
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
    })

    renderCollectiveOfferSummaryEdition(offer)

    const desactivateOffer = await screen.findByRole('button', {
      name: 'Mettre en pause',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should display bookable offer detail page when offer is bookable', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferFactory())

    expect(await screen.findByText('n°2')).toBeInTheDocument()
  })

  it('should not display bookable offer detail page when offer is template', async () => {
    renderCollectiveOfferSummaryEdition(getCollectiveOfferTemplateFactory())

    await waitFor(() =>
      expect(screen.queryByText('n°2')).not.toBeInTheDocument()
    )
  })

  it('should have the correct url for the list button when offer isTemplate is true', async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
    })

    renderCollectiveOfferSummaryEdition(offer)

    const listButton = await screen.findByRole('link', {
      name: /Retour à la liste des offres/i,
    })
    expect(listButton).toHaveAttribute('href', '/offres/vitrines')
  })
})
