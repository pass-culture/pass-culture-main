import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducational from '../'
import {
  defaultCreationProps,
  managedVenuesFactory,
  userOfferersFactory,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'
const eligibilityResponse = (
  eligible: boolean,
  override: Record<string, unknown> = {}
) => ({
  isOk: true,
  message: null,
  payload: { isOffererEligibleToEducationalOffer: eligible },
  ...override,
})

describe('screens | OfferEducational : creation offerer step', () => {
  let props: IOfferEducationalProps
  let getIsOffererEligible: IOfferEducationalProps['getIsOffererEligible']
  describe('when there is only one offerer associated with the account', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([{}]),
      }

      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(true))
    })

    it('should display offerer select with pre-selected options', async () => {
      renderWithProviders(<OfferEducational {...props} />)
      const offererSelect = await screen.findByLabelText('Structure')

      expect(offererSelect).toHaveValue(
        props.userOfferers[0].nonHumanizedId.toString()
      )
      expect(offererSelect).toBeDisabled()
      expect(offererSelect.children).toHaveLength(1)
    })

    it('should test eligibility and display venue input if offerer is eligible', async () => {
      renderWithProviders(
        <OfferEducational
          {...props}
          getIsOffererEligible={getIsOffererEligible}
        />
      )

      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)
      expect(await screen.findByLabelText('Lieu')).toBeInTheDocument()
    })

    it('should test eligibility and display an error message with a link if the offerer is not eligible', async () => {
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(false))

      renderWithProviders(
        <OfferEducational
          {...props}
          getIsOffererEligible={getIsOffererEligible}
        />
      )

      expect(
        await screen.findByText(
          'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByRole('link', { name: 'Faire une demande de référencement' })
      ).toBeInTheDocument()

      expect(screen.queryByLabelText('Lieu')).not.toBeInTheDocument()
    })
  })

  describe('when the offerer is not validated', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([{}]),
          },
        ]),
      }
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(false))
    })

    it('should display specific banner instead of place and referencing banner', async () => {
      renderWithProviders(<OfferEducational {...props} userOfferers={[]} />)
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
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([{}]),
          },
        ]),
      }
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(true))
    })

    it('should pre-select both selects and display the next step', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      const offerTypeTitle = await screen.findByRole('heading', {
        name: 'Type d’offre',
      })
      const offererSelect = await screen.findByLabelText('Structure')
      const venueSelect = await screen.findByLabelText('Lieu')

      expect(offererSelect).toBeInTheDocument()
      expect(offererSelect).toHaveValue(
        props.userOfferers[0].nonHumanizedId.toString()
      )
      expect(offererSelect.children).toHaveLength(1)
      expect(offererSelect).toBeDisabled()

      expect(screen.queryByTestId('error-offererId')).not.toBeInTheDocument()

      expect(venueSelect).toBeInTheDocument()
      expect(venueSelect).toHaveValue(
        props.userOfferers[0].managedVenues[0].nonHumanizedId.toString()
      )
      expect(venueSelect.children).toHaveLength(1)
      expect(venueSelect).toBeDisabled()
      expect(screen.queryByTestId('error-venueId')).not.toBeInTheDocument()

      expect(offerTypeTitle).toBeInTheDocument()
    })
  })

  describe('when there is multiple offerers associated with an account', () => {
    const firstOffererId = 1
    const secondOffererId = 2
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([
          { nonHumanizedId: firstOffererId },
          { nonHumanizedId: secondOffererId },
        ]),
      }

      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(true))
    })

    it('should require an offerer selection from the user and trigger eligibility check at selection', async () => {
      renderWithProviders(
        <OfferEducational
          {...props}
          getIsOffererEligible={getIsOffererEligible}
        />
      )
      const offererSelect = await screen.findByLabelText('Structure')

      expect(offererSelect).toBeInTheDocument()
      expect(offererSelect).toHaveValue('')
      expect(offererSelect.children).toHaveLength(3)
      expect(offererSelect).toBeEnabled()
      expect(screen.queryByTestId('error-offererId')).not.toBeInTheDocument()

      await userEvent.click(offererSelect)
      await userEvent.tab()

      await waitFor(() => expect(offererSelect).toBeInTheDocument())
      expect(
        await screen.findByText('Veuillez sélectionner une structure')
      ).toBeInTheDocument()

      expect(getIsOffererEligible).toHaveBeenCalledTimes(0)

      await userEvent.selectOptions(offererSelect, firstOffererId.toString())

      await userEvent.click(offererSelect)
      await userEvent.tab()

      expect(
        screen.queryByText('Veuillez sélectionner une structure')
      ).not.toBeInTheDocument()

      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)
      expect(getIsOffererEligible).toHaveBeenCalledWith(firstOffererId)
    })

    it('should check eligibility every time a diferent offerer is selected', async () => {
      renderWithProviders(
        <OfferEducational
          {...props}
          getIsOffererEligible={getIsOffererEligible}
        />
      )

      const offererSelect = await screen.findByLabelText('Structure')

      await userEvent.selectOptions(offererSelect, firstOffererId.toString())

      await userEvent.selectOptions(offererSelect, secondOffererId.toString())

      await waitFor(() => expect(getIsOffererEligible).toHaveBeenCalledTimes(2))
      expect(getIsOffererEligible).toHaveBeenCalledWith(secondOffererId)
      expect(getIsOffererEligible).toHaveBeenCalledWith(secondOffererId)
    })
  })

  describe('when there is multiple venues managed by an offerer', () => {
    const venue1Id = 1
    const venue2Id = 2
    const venue3Id = 3
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([
              { id: 'VENUE_1', name: 'Venue 1', nonHumanizedId: venue1Id },
              { id: 'VENUE_2', name: 'Venue 2', nonHumanizedId: venue2Id },
              { id: 'VENUE_3', name: 'A - Venue 3', nonHumanizedId: venue3Id },
            ]),
          },
        ]),
      }
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(true))
    })

    it('should require a venue selection from the user', async () => {
      renderWithProviders(<OfferEducational {...props} />)
      const venueSelect = await screen.findByLabelText('Lieu')

      expect(venueSelect).toHaveValue('')
      expect(venueSelect).toHaveDisplayValue('Sélectionner un lieu')
      expect(venueSelect.children).toHaveLength(4)
      expect(venueSelect).toBeEnabled()
      expect(screen.queryByTestId('error-venueId')).not.toBeInTheDocument()

      expect(
        screen.queryByRole('heading', {
          name: 'Type d’offre',
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
          name: 'Type d’offre',
        })
      ).toBeInTheDocument()
    })

    it('should display venues by alphabeticall order', async () => {
      renderWithProviders(<OfferEducational {...props} />)
      const venueSelect = await screen.findByLabelText('Lieu')
      const venuesOptions = venueSelect.children
      expect(venuesOptions[0].textContent).toEqual('Sélectionner un lieu')
      expect(venuesOptions[1].textContent).toEqual('A - Venue 3')
      expect(venuesOptions[2].textContent).toEqual('Venue 1')
      expect(venuesOptions[3].textContent).toEqual('Venue 2')
    })
  })
})
