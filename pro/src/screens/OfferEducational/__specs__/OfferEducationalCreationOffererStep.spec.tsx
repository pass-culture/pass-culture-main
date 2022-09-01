import '@testing-library/jest-dom'

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  defaultCreationProps,
  managedVenuesFactory,
  renderEACOfferForm,
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
      renderEACOfferForm(props)
      const offererSelect = await screen.findByLabelText('Structure')

      expect(offererSelect).toHaveValue('OFFERER_ID')
      expect(offererSelect).toBeDisabled()
      expect(offererSelect.children).toHaveLength(1)
    })

    it('should test eligibility and display venue input if offerer is eligible', async () => {
      renderEACOfferForm({ ...props, getIsOffererEligible })

      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)
      expect(
        await screen.findByLabelText('Lieu qui percevra le remboursement')
      ).toBeInTheDocument()
    })

    it('should test eligibility and display an error message with a link if the offerer is not eligible', async () => {
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(false))

      renderEACOfferForm({ ...props, getIsOffererEligible })

      expect(
        await screen.findByText(
          'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByRole('link', { name: 'Faire une demande de référencement' })
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText('Lieu qui percevra le remboursement')
      ).not.toBeInTheDocument()
    })
  })
  describe('when the offerer is not validated', () => {
    beforeEach(() => {
      props = {
        ...props,
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([{}]),
          },
        ]),
      }
    })

    it('should display specific banner instead of place and referencing banner', async () => {
      renderEACOfferForm({ ...props, userOfferers: [] })
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
        ...props,
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([{}]),
          },
        ]),
      }
    })

    it('should pre-select both selects and display the next step', async () => {
      renderEACOfferForm(props)
      const offerTypeTitle = await screen.findByRole('heading', {
        name: 'Type d’offre',
      })
      const offererSelect = await screen.findByLabelText('Structure')
      const venueSelect = await screen.findByLabelText(
        'Lieu qui percevra le remboursement'
      )

      expect(offererSelect).toBeInTheDocument()
      expect(offererSelect).toHaveValue('OFFERER_ID')
      expect(offererSelect.children).toHaveLength(1)
      expect(offererSelect).toBeDisabled()

      expect(screen.queryByTestId('error-offererId')).not.toBeInTheDocument()

      expect(venueSelect).toBeInTheDocument()
      expect(venueSelect).toHaveValue('VENUE_ID')
      expect(venueSelect.children).toHaveLength(1)
      expect(venueSelect).toBeDisabled()
      expect(screen.queryByTestId('error-venueId')).not.toBeInTheDocument()

      expect(offerTypeTitle).toBeInTheDocument()
    })
  })

  describe('when there is multiple offerers associated with an account', () => {
    beforeEach(() => {
      props = {
        ...props,
        userOfferers: userOfferersFactory([
          { id: 'OFFERER_1' },
          { id: 'OFFERER_2' },
        ]),
      }

      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(true))
    })
    it('should require an offerer selection from the user and trigger eligibility check at selection', async () => {
      renderEACOfferForm({ ...props, getIsOffererEligible })
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

      await userEvent.selectOptions(offererSelect, 'OFFERER_1')

      expect(
        screen.queryByText('Veuillez sélectionner une structure')
      ).not.toBeInTheDocument()

      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)
      expect(getIsOffererEligible).toHaveBeenCalledWith('OFFERER_1')
    })

    it('should check eligibility every time a diferent offerer is selected', async () => {
      renderEACOfferForm({ ...props, getIsOffererEligible })

      const offererSelect = await screen.findByLabelText('Structure')

      await userEvent.selectOptions(offererSelect, 'OFFERER_1')

      await userEvent.selectOptions(offererSelect, 'OFFERER_2')

      await waitFor(() => expect(getIsOffererEligible).toHaveBeenCalledTimes(2))

      expect(getIsOffererEligible).toHaveBeenCalledWith('OFFERER_1')
      expect(getIsOffererEligible).toHaveBeenCalledWith('OFFERER_2')
    })
  })

  describe('when there is multiple venues managed by an offerer', () => {
    beforeEach(() => {
      props = {
        ...props,
        userOfferers: userOfferersFactory([
          {
            managedVenues: managedVenuesFactory([
              { id: 'VENUE_1', name: 'Venue 1' },
              { id: 'VENUE_2', name: 'Venue 2' },
            ]),
          },
        ]),
      }
    })
    it('should require a venue selection from the user', async () => {
      renderEACOfferForm(props)
      const venueSelect = await screen.findByLabelText(
        'Lieu qui percevra le remboursement'
      )

      expect(venueSelect).toHaveValue('')
      expect(venueSelect).toHaveDisplayValue('Sélectionner un lieu')
      expect(venueSelect.children).toHaveLength(3)
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

      await userEvent.selectOptions(venueSelect, 'VENUE_1')

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
  })
})
