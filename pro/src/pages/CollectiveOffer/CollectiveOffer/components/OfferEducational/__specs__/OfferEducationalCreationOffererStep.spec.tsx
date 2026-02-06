import { screen } from '@testing-library/react'

import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenuesFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
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
        selectedVenue: makeGetVenueResponseModel({ id: props.venues[0].id }),
        venues: [...props.venues],
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

  describe('when there is multiple venues managed by an offerer', () => {
    it('should display venues by alphabetical order', async () => {
      const venues = [
        makeVenueListItem({ id: 1 }),
        makeVenueListItem({ id: 2 }),
        makeVenueListItem({ id: 3 }),
      ]

      const props: OfferEducationalProps = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({
          managedVenues: managedVenuesFactory([
            { name: 'Venue 1', id: 1 },
            { name: 'Venue 2', id: 2 },
            { name: 'A - Venue 3', id: 3 },
          ]),
        }),
        venues,
      }

      renderOfferEducational(props)

      const venueSelect = await screen.findByLabelText(/Structure/)
      const venuesOptions = venueSelect.children
      expect(venuesOptions[0].textContent).toEqual('Sélectionner une structure')
      expect(venuesOptions[1].textContent).toEqual('A - Venue 3')
      expect(venuesOptions[2].textContent).toEqual('Venue 1')
      expect(venuesOptions[3].textContent).toEqual('Venue 2')
    })
  })
})
