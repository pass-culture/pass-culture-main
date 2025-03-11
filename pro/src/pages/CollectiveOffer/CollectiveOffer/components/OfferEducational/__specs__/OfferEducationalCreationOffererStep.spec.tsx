import { screen } from '@testing-library/react'

import * as hooks from 'commons/hooks/swr/useOfferer'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  managedVenuesFactory,
  userOffererFactory,
} from 'commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

function renderOfferEducational(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
  })
}

describe('screens | OfferEducational : creation offerer step', () => {
  let props: OfferEducationalProps
  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  describe('when the offerer is not validated', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({
          managedVenues: managedVenuesFactory([{}]),
        }),
      }
    })

    it('should display specific banner instead of place and referencing banner', async () => {
      renderWithProviders(<OfferEducational {...props} userOfferer={null} />)
      expect(
        await screen.findByText(
          /Vous ne pouvez pas créer d’offre collective tant que votre entité juridique n’est pas validée./
        )
      ).toBeInTheDocument()
    })
  })

  describe('when there is multiple venues managed by an offerer', () => {
    const venue1Id = 1
    const venue2Id = 2
    const venue3Id = 3
    beforeEach(() => {
      vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)

      props = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({
          managedVenues: managedVenuesFactory([
            { name: 'Venue 1', id: venue1Id },
            { name: 'Venue 2', id: venue2Id },
            { name: 'A - Venue 3', id: venue3Id },
          ]),
        }),
      }
    })

    it('should display venues by alphabeticall order', async () => {
      renderOfferEducational(props)
      const venueSelect = await screen.findByLabelText('Structure *')
      const venuesOptions = venueSelect.children
      expect(venuesOptions[0].textContent).toEqual('Sélectionner une structure')
      expect(venuesOptions[1].textContent).toEqual('A - Venue 3')
      expect(venuesOptions[2].textContent).toEqual('Venue 1')
      expect(venuesOptions[3].textContent).toEqual('Venue 2')
    })
  })
})
