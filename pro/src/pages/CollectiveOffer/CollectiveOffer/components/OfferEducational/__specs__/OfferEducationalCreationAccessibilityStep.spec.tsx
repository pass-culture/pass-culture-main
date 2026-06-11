import { screen, waitFor } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { userOffererFactory } from '@/commons/utils/factories/userOfferersFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import {
  OfferEducational,
  type OfferEducationalProps,
} from '../OfferEducational'

function renderComponent(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 13,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: false,
          audioDisabilityCompliant: false,
        }),
      },
    },
  })
}

describe('screens | OfferEducational : accessibility step', () => {
  let props: OfferEducationalProps

  const offererId = 15

  beforeEach(() => {
    props = {
      ...defaultCreationProps,
    }
  })

  it('should prefill intervention and accessibility fields with venue intervention field when selecting venue', async () => {
    props.userOfferer = userOffererFactory({
      id: offererId,
    })
    renderComponent(props)

    await waitFor(() => {
      expect(
        screen.queryAllByRole('checkbox', {
          checked: true,
        })
      ).toHaveLength(2)
    })
  })
})
