import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { defaultAdageUser } from 'commons/utils/factories/adageFactories'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'

import { AdagePreviewLayout } from '../AdagePreviewLayout'

function renderAdagePreviewLayout(
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel = getCollectiveOfferTemplateFactory()
) {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdagePreviewLayout offer={offer} />
    </AdageUserContextProvider>
  )
}

describe('AdagePreviewLayout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
      city: 'Montpellier',
    })
  })

  it('should show a preview of the offer template', async () => {
    renderAdagePreviewLayout({
      ...getCollectiveOfferTemplateFactory(),
      name: 'My test name',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name' })
    ).toBeInTheDocument()
  })

  it('should show a preview of the offer bookable', async () => {
    renderAdagePreviewLayout({
      ...getCollectiveOfferFactory(),
      name: 'My test name bookable',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name bookable' })
    ).toBeInTheDocument()
  })

  it('should display the venue location infos if the offer happens at the offerer place', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    renderAdagePreviewLayout({
      ...offer,
      offerVenue: {
        ...offer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
        venueId: 1,
      },
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/à Montpellier/)).toBeInTheDocument()
  })
})
