import { axe } from 'vitest-axe'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformationsEdition } from './CollectiveOfferInformationsEdition'

const renderCollectiveOfferInformationEdition = () => {
  const offer = getCollectiveOfferFactory()
  const venue = makeGetVenueResponseModel({ id: 1, allowedOnAdage: true })
  return renderWithProviders(
    <CollectiveOfferInformationsEdition offer={offer} />,
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
describe('<CollectiveOfferInformationsEdition />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferInformationEdition()

    expect(await axe(container)).toHaveNoViolations()
  })
})
