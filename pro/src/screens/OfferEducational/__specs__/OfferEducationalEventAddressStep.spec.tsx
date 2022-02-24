import '@testing-library/jest-dom'
import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { triggerFieldValidation } from 'ui-kit/form/__tests-utils__'

import {
  defaultCreationProps,
  renderEACOfferForm,
  elements,
  categoriesFactory,
  subCategoriesFactory,
  userOfferersFactory,
  managedVenueFactory,
} from '../__tests-utils__'
import { IOfferEducationalProps } from '../OfferEducational'

const {
  queryOffererSelect,
  queryOfferVenueRadioButtons,
  queryOfferVenueSelect,
  queryOfferVenueTextArea,
  queryOfferVenueAddressDisplay,
  queryVenueSelect,
} = elements

describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps

  describe('when there is only one venue managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1' },
        ]),
      }
    })

    it('should display venue radio buttons with pre-selected offerer venue and a disabled select', async () => {
      renderEACOfferForm(props)

      // wait for page to be rendered
      const offererSelect = queryOffererSelect()
      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      const { offererVenueRadio, schoolRadio, otherRadio } =
        queryOfferVenueRadioButtons()

      const offerVenueSelect = queryOfferVenueSelect()
      const offerVenueAddressDisplay = queryOfferVenueAddressDisplay()

      expect(offererVenueRadio.input?.checked).toBe(true)
      expect(schoolRadio.input?.checked).toBe(false)
      expect(otherRadio.input?.checked).toBe(false)
      expect(offerVenueSelect.input?.value).toBe('VENUE_ID')
      expect(offerVenueSelect.input).toBeDisabled()
      expect(offerVenueSelect.input?.options).toHaveLength(1)
      expect(offerVenueSelect.isOptionnal).toBe(false)
      expect(offerVenueAddressDisplay).toBeInTheDocument()
    })

    it('should display text area when user selects "other"', async () => {
      renderEACOfferForm(props)

      // wait for page to be rendered
      const offererSelect = queryOffererSelect()
      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      const { offererVenueRadio, schoolRadio, otherRadio } =
        queryOfferVenueRadioButtons()

      userEvent.click(otherRadio.input as HTMLInputElement)

      const offerVenueSelect = queryOfferVenueSelect()
      const offerVenueTextArea = queryOfferVenueTextArea()

      expect(offererVenueRadio.input?.checked).toBe(false)
      expect(schoolRadio.input?.checked).toBe(false)
      expect(otherRadio.input?.checked).toBe(true)
      expect(offerVenueSelect.input).not.toBeInTheDocument()
      expect(offerVenueTextArea.input).toBeInTheDocument()
    })

    it('should not display neither event venue address nor text area if user selects "school"', async () => {
      renderEACOfferForm(props)

      // wait for page to be rendered
      const offererSelect = queryOffererSelect()
      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      const { offererVenueRadio, schoolRadio, otherRadio } =
        queryOfferVenueRadioButtons()

      userEvent.click(schoolRadio.input as HTMLInputElement)

      const offerVenueSelect = queryOfferVenueSelect()
      const offerVenueTextArea = queryOfferVenueTextArea()

      expect(offererVenueRadio.input?.checked).toBe(false)
      expect(schoolRadio.input?.checked).toBe(true)
      expect(otherRadio.input?.checked).toBe(false)
      expect(offerVenueSelect.input).not.toBeInTheDocument()
      expect(offerVenueTextArea.input).not.toBeInTheDocument()
    })
  })

  describe('when there are multiple venues managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([
          {
            id: 'OFFERER_1',
            managedVenues: [
              managedVenueFactory({ id: 'VENUE_1' }),
              managedVenueFactory({ id: 'VENUE_2' }),
            ],
          },
        ]),
        educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1' },
        ]),
      }
    })

    it('should require an offer venue selection from the user', async () => {
      renderEACOfferForm(props)

      // wait for page to be rendered
      const offererSelect = queryOffererSelect()
      await waitFor(() => expect(offererSelect.input).toBeInTheDocument())

      const venueSelect = queryVenueSelect()
      await waitFor(() => expect(venueSelect.input).toBeInTheDocument())
      userEvent.selectOptions(venueSelect.input as HTMLSelectElement, 'VENUE_1')

      const offerVenueSelect = queryOfferVenueSelect()

      expect(offerVenueSelect.input?.value).toBe('')

      triggerFieldValidation(offerVenueSelect.input as HTMLSelectElement)

      await waitFor(() =>
        expect(offerVenueSelect.getError()).toBeInTheDocument()
      )
      expect(offerVenueSelect.getError()).toHaveTextContent(
        'Veuillez sélectionner un lieu'
      )
      userEvent.selectOptions(
        offerVenueSelect.input as HTMLSelectElement,
        'VENUE_1'
      )
      await waitFor(() =>
        expect(offerVenueSelect.getError()).not.toBeInTheDocument()
      )

      expect(offerVenueSelect.input?.options).toHaveLength(3)
    })
  })
})
