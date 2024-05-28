import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { Mode } from 'core/OfferEducational/types'
import { getCollectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { CollectiveOfferSummaryEditionScreen } from '../CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderCollectiveOfferSummaryEdition = (
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
) => {
  renderWithProviders(
    <CollectiveOfferSummaryEditionScreen offer={offer} mode={Mode.EDITION} />,
    { user: sharedCurrentUserFactory() }
  )
}

describe('CollectiveOfferSummary', () => {
  let offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel

  it('should display desactive offer option when offer is active and not booked', async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
      isActive: true,
    })

    renderCollectiveOfferSummaryEdition(offer)
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur ADAGE',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })
})
