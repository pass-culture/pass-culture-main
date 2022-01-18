import '@testing-library/jest-dom'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import merge from 'lodash/merge'

import {
  defaultCreationProps,
  renderEACOfferForm,
  userOfferersFactory,
  managedVenuesFactory,
  elements,
  triggerFieldValidation,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

const {
  queryOffererSelect,
  queryVenueSelect,
  findOfferTypeTitle,
  queryOfferTypeTitle,
} = elements

const eligibilityResponse = (
  eligible: boolean,
  override: Record<string, unknown> = {}
) =>
  merge(
    {},
    {
      isOk: true,
      message: null,
      payload: { isOffererEligibleToEducationalOffer: eligible },
    },
    override
  )

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
      const offererSelect = queryOffererSelect()

      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      expect(offererSelect.input?.value).toBe('OFFERER_ID')
      expect(offererSelect.input).toBeDisabled()
      expect(offererSelect.input?.options).toHaveLength(1)
      expect(offererSelect.isOptionnal).toBe(false)
    })

    it('should test eligibility and display venue input if offerer is eligible', async () => {
      renderEACOfferForm({ ...props, getIsOffererEligible })
      const offererSelect = queryOffererSelect()

      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())
      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)

      const venueSelect = queryVenueSelect()
      expect(venueSelect.input).toBeInTheDocument()
    })

    it('should test eligibility and display an error message with a link if the offerer is not eligible', async () => {
      getIsOffererEligible = jest
        .fn()
        .mockResolvedValue(eligibilityResponse(false))

      renderEACOfferForm({ ...props, getIsOffererEligible })
      const offererSelect = queryOffererSelect()

      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      expect(
        screen.getByText(
          'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByRole('link', { name: 'Faire une demande de référencement' })
      ).toBeInTheDocument()

      expect(queryVenueSelect().input).not.toBeInTheDocument()
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
      const offerTypeTitle = await findOfferTypeTitle()

      const offererSelect = queryOffererSelect()
      const venueSelect = queryVenueSelect()

      expect(offererSelect.input).toBeInTheDocument()
      expect(offererSelect.input).toHaveValue('OFFERER_ID')
      expect(offererSelect.input?.options).toHaveLength(1)
      expect(offererSelect.input).toBeDisabled()
      expect(offererSelect.isOptionnal).toBeFalsy()
      expect(offererSelect.getError()).not.toBeInTheDocument()

      expect(venueSelect.input).toBeInTheDocument()
      expect(venueSelect.input).toHaveValue('VENUE_ID')
      expect(venueSelect.input?.options).toHaveLength(1)
      expect(venueSelect.input).toBeDisabled()
      expect(venueSelect.isOptionnal).toBeFalsy()
      expect(venueSelect.getError()).not.toBeInTheDocument()

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
      const offererSelect = queryOffererSelect()

      expect(offererSelect.input).toBeInTheDocument()
      expect(offererSelect.input).toHaveValue('')
      expect(offererSelect.input?.options).toHaveLength(3)
      expect(offererSelect.input).toBeEnabled()
      expect(offererSelect.isOptionnal).toBeFalsy()
      expect(offererSelect.getError()).not.toBeInTheDocument()

      triggerFieldValidation(offererSelect.input as HTMLSelectElement)

      await waitFor(() => expect(offererSelect.getError()).toBeInTheDocument())
      expect(offererSelect.getError()).toHaveTextContent(
        'Veuillez sélectionner une structure'
      )

      expect(getIsOffererEligible).toHaveBeenCalledTimes(0)

      userEvent.selectOptions(
        offererSelect.input as HTMLSelectElement,
        'OFFERER_1'
      )

      await waitFor(() =>
        expect(offererSelect.getError()).not.toBeInTheDocument()
      )

      expect(getIsOffererEligible).toHaveBeenCalledTimes(1)
      expect(getIsOffererEligible).toHaveBeenCalledWith('OFFERER_1')
    })

    it('should check eligibility every time a diferent offerer is selected', async () => {
      renderEACOfferForm({ ...props, getIsOffererEligible })

      const offererSelect = queryOffererSelect()

      userEvent.selectOptions(
        offererSelect.input as HTMLSelectElement,
        'OFFERER_1'
      )

      userEvent.selectOptions(
        offererSelect.input as HTMLSelectElement,
        'OFFERER_2'
      )

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

      await waitFor(() => expect(queryVenueSelect().input).toBeInTheDocument())

      const venueSelect = queryVenueSelect()
      expect(venueSelect.input).toBeInTheDocument()
      expect(venueSelect.input).toHaveValue('')
      expect(venueSelect.input).toHaveDisplayValue('Sélectionner un lieu')
      expect(venueSelect.input?.options).toHaveLength(3)
      expect(venueSelect.input).toBeEnabled()
      expect(venueSelect.isOptionnal).toBeFalsy()
      expect(venueSelect.getError()).not.toBeInTheDocument()

      expect(queryOfferTypeTitle()).not.toBeInTheDocument()

      triggerFieldValidation(venueSelect.input as HTMLSelectElement)

      await waitFor(() => expect(venueSelect.getError()).toBeInTheDocument())
      expect(venueSelect.getError()).toHaveTextContent(
        'Veuillez sélectionner un lieu'
      )

      userEvent.selectOptions(venueSelect.input as HTMLSelectElement, 'VENUE_1')

      await waitFor(() =>
        expect(venueSelect.getError()).not.toBeInTheDocument()
      )

      expect(venueSelect.input).toHaveDisplayValue('Venue 1')

      expect(queryOfferTypeTitle()).toBeInTheDocument()
    })
  })
})
