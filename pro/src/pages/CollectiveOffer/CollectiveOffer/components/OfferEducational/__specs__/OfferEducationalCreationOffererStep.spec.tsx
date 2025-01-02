import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
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
      offerer: { selectedOffererId: 1, offererNames: [] },
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

      expect(await screen.findByLabelText('Lieu *')).toBeInTheDocument()
    })

    it('should test eligibility and display an error message with a link if the offerer is not eligible', async () => {
      renderWithProviders(
        <OfferEducational
          {...props}
          userOfferer={userOffererFactory({ allowedOnAdage: false })}
        />
      )

      expect(
        await screen.findByText(
          'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByRole('link', { name: /Faire une demande de référencement/ })
      ).toBeInTheDocument()

      expect(screen.queryByLabelText('Lieu')).not.toBeInTheDocument()
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
          /Vous ne pouvez pas créer d’offre collective tant que votre structure n’est pas validée./
        )
      ).toBeInTheDocument()
      expect(
        screen.queryByText(
          /Pour proposer des offres à destination d’un groupe scolaire, vous devez renseigner un lieu pour pouvoir être remboursé./
        )
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(
          /Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé/
        )
      ).not.toBeInTheDocument()
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

      const venueSelect = await screen.findByLabelText('Lieu *')

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

    it('should require a venue selection from the user', async () => {
      renderOfferEducational(props)
      const venueSelect = await screen.findByLabelText('Lieu *')

      expect(venueSelect).toHaveValue('')
      expect(venueSelect).toHaveDisplayValue('Sélectionner un lieu')
      expect(venueSelect.children).toHaveLength(4)
      expect(venueSelect).toBeEnabled()
      expect(screen.queryByTestId('error-venueId')).not.toBeInTheDocument()

      expect(
        screen.queryByRole('heading', {
          name: 'Quel est le type de votre offre ?',
        })
      ).not.toBeInTheDocument()

      await userEvent.click(venueSelect)
      await userEvent.tab()

      expect(
        await screen.findByText('Veuillez sélectionner un lieu')
      ).toBeInTheDocument()

      await userEvent.selectOptions(venueSelect, venue1Id.toString())

      expect(
        screen.queryByText('Veuillez sélectionner un lieu')
      ).not.toBeInTheDocument()

      expect(venueSelect).toHaveDisplayValue('Venue 1')

      expect(
        await screen.findByRole('heading', {
          name: 'Quel est le type de votre offre ?',
        })
      ).toBeInTheDocument()
    })

    it('should display venues by alphabeticall order', async () => {
      renderOfferEducational(props)
      const venueSelect = await screen.findByLabelText('Lieu *')
      const venuesOptions = venueSelect.children
      expect(venuesOptions[0].textContent).toEqual('Sélectionner un lieu')
      expect(venuesOptions[1].textContent).toEqual('A - Venue 3')
      expect(venuesOptions[2].textContent).toEqual('Venue 1')
      expect(venuesOptions[3].textContent).toEqual('Venue 2')
    })
  })
})
