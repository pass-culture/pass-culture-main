import { screen } from '@testing-library/react'

import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
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

function renderOfferEducational(props: OfferEducationalProps) {
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
      offerer: currentOffererFactory(),
    },
  })
}

describe('screens | OfferEducational : creation offerer step', () => {
  describe('when the offerer is not validated', () => {
    it('should display specific banner instead of place and referencing banner', async () => {
      const venues = [makeVenueListItem({ id: 1 })]

      const props: OfferEducationalProps = {
        ...defaultCreationProps,
        userOfferer: null,
        venues,
      }

      renderOfferEducational(props)

      expect(
        await screen.findByText(
          /La création d'offres collectives nécessite la validation de votre entité juridique./
        )
      ).toBeInTheDocument()
    })
  })
})
