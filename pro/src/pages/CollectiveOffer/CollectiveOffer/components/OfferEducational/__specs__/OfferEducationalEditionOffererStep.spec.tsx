import { screen, waitFor } from '@testing-library/react'

import { Mode } from '@/commons/core/OfferEducational/types'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__/defaultProps'
import {
  OfferEducational,
  type OfferEducationalProps,
} from '../OfferEducational'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))

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

describe('screens | OfferEducational : edition offerer step', () => {
  let props: OfferEducationalProps

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should show banner if generate from publicApi', async () => {
    props.mode = Mode.EDITION
    props.offer = getCollectiveOfferFactory({ isPublicApi: true })
    renderComponent(props)
    await waitFor(() => {
      expect(
        screen.getByText(
          'Cette offre a été importée automatiquement depuis votre système de billetterie.'
        )
      ).toBeInTheDocument()
    })
  })
})
