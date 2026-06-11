import { screen } from '@testing-library/react'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
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
          id: 1,
        }),
      },
    },
  })
}

describe('screens | OfferEducational : creation offerer step', () => {
  describe('when the offerer is not validated', () => {
    it('should display specific banner instead of place and referencing banner', async () => {
      const props: OfferEducationalProps = {
        ...defaultCreationProps,
        userOfferer: null,
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
