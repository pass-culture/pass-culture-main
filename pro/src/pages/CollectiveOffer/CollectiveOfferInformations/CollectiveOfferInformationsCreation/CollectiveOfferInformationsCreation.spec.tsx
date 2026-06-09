import { axe } from 'vitest-axe'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformationsCreation } from './CollectiveOfferInformationsCreation'

const renderCollectiveOfferInformationCreation = () => {
  const offer = getCollectiveOfferFactory()
  const venue = makeGetVenueResponseModel({ id: 1, allowedOnAdage: true })
  return renderWithProviders(
    <CollectiveOfferInformationsCreation offer={offer} />,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: venue,
        },
      },
    }
  )
}

describe('<CollectiveOfferInformationsCreation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferInformationCreation()

    expect(await axe(container)).toHaveNoViolations()
  })
})
