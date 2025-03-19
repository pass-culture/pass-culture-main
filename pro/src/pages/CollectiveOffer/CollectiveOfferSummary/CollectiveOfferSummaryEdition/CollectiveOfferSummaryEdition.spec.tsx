import { screen } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { getCollectiveOfferTemplateFactory } from 'commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { managedVenueFactory, userOffererFactory } from 'commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOfferSummaryEdition } from './CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('apiClient/api', () => ({
  api: {
    listEducationalOfferers: vi.fn(),
  },
}))

const renderCollectiveOfferSummaryEdition = (
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
) => {
  renderWithProviders(<CollectiveOfferSummaryEdition offer={offer} />, {
    user: sharedCurrentUserFactory(),
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

  it('should display desactive offer option when offer is active and not booked', async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
      isActive: true,
    })

    renderCollectiveOfferSummaryEdition(offer)

    const desactivateOffer = await screen.findByRole('button', {
      name: 'Masquer la publication sur ADAGE',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })
})
