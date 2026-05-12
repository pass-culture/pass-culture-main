import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
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
          id: props.venues[0].id,
        }),
        venues: [
          ...props.venues.map((venue) =>
            makeVenueListItemLiteResponseModel({ id: venue.id })
          ),
        ],
      },
    },
  })
}

describe('screens | OfferEducational : accessibility step', () => {
  let props: OfferEducationalProps

  const firstVenueId = 43
  const secondVenueId = 13
  const offererId = 15

  beforeEach(() => {
    props = {
      ...defaultCreationProps,
    }

    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({ id: firstVenueId }),
        makeVenueListItem({ id: secondVenueId }),
      ],
    })
  })

  it('should prefill intervention and accessibility fields with venue intervention field when selecting venue', async () => {
    props = {
      ...props,
      venues: [
        makeVenueListItem({ id: firstVenueId }),
        makeVenueListItem({ id: secondVenueId }),
      ],
    }

    props.userOfferer = userOffererFactory({
      id: offererId,
      managedVenues: [
        managedVenueFactory({}),
        managedVenueFactory({
          id: firstVenueId,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: false,
          audioDisabilityCompliant: false,
        }),
      ],
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
