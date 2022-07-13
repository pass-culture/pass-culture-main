import '@testing-library/jest-dom'

import {
  categoriesFactory,
  defaultCreationProps,
  managedVenueFactory,
  renderEACOfferForm,
  subCategoriesFactory,
  userOfferersFactory,
} from '../__tests-utils__'
import { screen, waitFor } from '@testing-library/react'

import { IOfferEducationalProps } from '../OfferEducational'
import userEvent from '@testing-library/user-event'

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
      expect(screen.getByLabelText('Structure')).toBeInTheDocument()

      expect(await screen.findByLabelText('Dans votre lieu')).toBeChecked()
      expect(
        screen.getByLabelText('Dans l’établissement scolaire')
      ).not.toBeChecked()
      expect(screen.getByLabelText('Autre')).not.toBeChecked()

      expect(screen.getByLabelText('Sélectionner le lieu')).toHaveValue(
        'VENUE_ID'
      )
      expect(screen.getByLabelText('Sélectionner le lieu')).toBeDisabled()

      expect(
        screen.getByText('Venue name', { exact: false, selector: 'p' })
      ).toBeInTheDocument()
    })

    it('should display text area when user selects "other"', async () => {
      renderEACOfferForm(props)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner le lieu')
      ).not.toBeInTheDocument()

      expect(
        screen.getByLabelText('Adresse de l’évènement')
      ).toBeInTheDocument()
    })

    it('should not display neither event venue address nor text area if user selects "school"', async () => {
      renderEACOfferForm(props)

      await userEvent.click(
        await screen.findByLabelText('Dans l’établissement scolaire')
      )
      expect(
        screen.getByLabelText('Dans l’établissement scolaire')
      ).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner le lieu')
      ).not.toBeInTheDocument()

      expect(
        screen.queryByLabelText('Adresse de l’évènement')
      ).not.toBeInTheDocument()
    })
  })
  // TO DO: move this test, it does not belong to Address step
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
      const offererSelect = await screen.findByLabelText(
        'Lieu qui percevra le remboursement'
      )
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, ['VENUE_1'])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner le lieu'
      )
      expect(offerVenueSelect).toHaveValue('')
      expect(offerVenueSelect.children).toHaveLength(3)
      await userEvent.selectOptions(offerVenueSelect, 'VENUE_1')
      expect(offerVenueSelect).toHaveValue('VENUE_1')

      await userEvent.selectOptions(offerVenueSelect, '')
      await userEvent.tab()

      expect(offerVenueSelect).toHaveValue('')

      await waitFor(() =>
        expect(
          screen.getByText(/Veuillez sélectionner un lieu/)
        ).toBeInTheDocument()
      )
    })
  })
})
