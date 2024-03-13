import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferTemplateResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import {
  defaultGetVenue,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import AdagePreviewLayout from '../AdagePreviewLayout'

function renderAdagePreviewLayout(
  offer: GetCollectiveOfferTemplateResponseModel = getCollectiveOfferTemplateFactory()
) {
  renderWithProviders(<AdagePreviewLayout offer={offer} />)
}

describe('AdagePreviewLayout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
      city: 'Montpellier',
    })
  })

  it('should show a preview of the offer', async () => {
    renderAdagePreviewLayout({
      ...getCollectiveOfferTemplateFactory(),
      name: 'My test name',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name' })
    ).toBeInTheDocument()
  })

  it('should display the venue location infos if the offer happens at the offerer place', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderAdagePreviewLayout({
      ...offer,
      offerVenue: {
        ...offer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
      },
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/à Montpellier/)).toBeInTheDocument()
  })
})
