import { screen } from '@testing-library/dom'

import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformation } from './CollectiveOfferInformation'

vi.mock(
  './components/CollectiveOfferInformationForm/CollectiveOfferInformationForm',
  () => ({
    CollectiveOfferInformationForm: vi.fn(() => (
      <div data-testid="infos-form" />
    )),
  })
)

const renderCollectiveOfferInformation = (
  offer: GetCollectiveOfferResponseModel
) => {
  const venue = makeGetVenueResponseModel({ id: 1, allowedOnAdage: true })
  return renderWithProviders(<CollectiveOfferInformation offer={offer} />, {
    initialRouterEntries: [`/offre/${offer.id}/collectif/stocks`],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: venue,
      },
    },
  })
}

describe('<CollectiveOfferInformation />', () => {
  it('should render CollectiveOfferInformationForm', () => {
    const offer = getCollectiveOfferFactory()
    renderCollectiveOfferInformation(offer)

    expect(screen.getByTestId('infos-form')).toBeVisible()
  })
})
