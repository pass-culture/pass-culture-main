import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import createFetchMock from 'vitest-fetch-mock'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { Mode } from 'core/OfferEducational'
import { getCollectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummaryEdition from '../CollectiveOfferSummaryEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderCollectiveOfferSummaryEdition = (
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(
    <CollectiveOfferSummaryEdition
      offer={offer}
      reloadCollectiveOffer={vi.fn()}
      mode={Mode.EDITION}
    />,
    { storeOverrides }
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
      name: 'Masquer la publication sur Adage',
    })
    expect(desactivateOffer).toBeInTheDocument()
  })
})
