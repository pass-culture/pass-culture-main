import { screen } from '@testing-library/react'

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
  describe('when there is only one offerer associated with the account', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({}),
      }
    })

    it('should test eligibility and display venue input if offerer is eligible', async () => {
      renderOfferEducational(props)

      expect(await screen.findByLabelText('Structure *')).toBeInTheDocument()
    })
  })

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

  describe('when there is only one managed venue associated with the offerer and offerer is eligible', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({
          managedVenues: managedVenuesFactory([{}]),
        }),
      }
    })

    it('should select venue and display the next step', async () => {
      renderOfferEducational(props)

      const offerTypeTitle = await screen.findByRole('heading', {
        name: 'Quel est le type de votre offre ?',
      })

      const venueSelect = await screen.findByLabelText('Structure *')

      expect(venueSelect).toBeInTheDocument()
      expect(venueSelect).toHaveValue(
        props.userOfferer?.managedVenues[0].id.toString()
      )
      expect(venueSelect.children).toHaveLength(1)
      expect(venueSelect).toBeDisabled()
      expect(screen.queryByTestId('error-venueId')).not.toBeInTheDocument()

      expect(offerTypeTitle).toBeInTheDocument()
    })
  })

  describe('when there is multiple venues managed by an offerer', () => {
    const venue1Id = 1
    const venue2Id = 2
    const venue3Id = 3
    beforeEach(() => {
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
