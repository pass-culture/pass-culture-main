import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import {
  categoriesFactory,
  defaultCreationProps,
  managedVenueFactory,
  subCategoriesFactory,
  userOfferersFactory,
} from '../__tests-utils__'
import { userOffererFactory } from '../__tests-utils__/userOfferersFactory'
import { INTERVENTION_AREA_LABEL } from '../constants/labels'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps

  describe('when there is only one venue managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        categories: {
          educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
          educationalSubCategories: subCategoriesFactory([
            { categoryId: 'CAT_1', id: 'SUBCAT_1' },
          ]),
        },
      }
    })

    it('should display venue radio buttons with pre-selected offerer venue and a disabled select', async () => {
      renderWithProviders(<OfferEducational {...props} />)
      // wait for page to be rendered
      expect(screen.getByLabelText('Structure')).toBeInTheDocument()

      expect(await screen.findByLabelText('Dans votre lieu')).toBeChecked()
      expect(
        screen.getByLabelText('Dans l’établissement scolaire')
      ).not.toBeChecked()
      expect(screen.getByLabelText('Autre')).not.toBeChecked()

      expect(screen.getByLabelText('Sélectionner le lieu')).toHaveValue('1')
      expect(screen.getByLabelText('Sélectionner le lieu')).toBeDisabled()

      expect(
        await screen.findByText('Venue name', { exact: false, selector: 'div' })
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).not.toBeInTheDocument()
    })

    it('should display text area + intervention area multiselect when user selects "other"', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner le lieu')
      ).not.toBeInTheDocument()

      expect(
        screen.getByLabelText('Adresse de l’évènement')
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).toBeInTheDocument()
    })

    it('should not display neither event venue address nor text area if user selects "school"', async () => {
      renderWithProviders(<OfferEducational {...props} />)

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

      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).toBeInTheDocument()
    })
  })
  // TO DO: move this test, it does not belong to Address step
  describe('when there are multiple venues managed by the offerer', () => {
    const firstVenueId = '12'
    const secondVenueId = '23'
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        userOfferers: userOfferersFactory([
          {
            id: '1',
            nonHumanizedId: 1,
            managedVenues: [
              managedVenueFactory({
                id: firstVenueId,
                nonHumanizedId: Number(firstVenueId),
              }),
              managedVenueFactory({
                id: secondVenueId,
                nonHumanizedId: Number(secondVenueId),
              }),
            ],
          },
        ]),
        categories: {
          educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
          educationalSubCategories: subCategoriesFactory([
            { categoryId: 'CAT_1', id: 'SUBCAT_1' },
          ]),
        },
      }
    })

    it('should require an offer venue selection from the user', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      // wait for page to be rendered
      const offererSelect = await screen.findByLabelText('Lieu')
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, [firstVenueId])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner le lieu'
      )
      expect(offerVenueSelect).toHaveValue(firstVenueId)
      expect(offerVenueSelect.children).toHaveLength(3)

      await userEvent.selectOptions(offerVenueSelect, secondVenueId)
      await userEvent.selectOptions(offerVenueSelect, '')
      await userEvent.tab()

      expect(offerVenueSelect).toHaveValue(firstVenueId)
    })

    it('should prefill the venue data when switching from one event adress type to offerer venue type', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      // wait for page to be rendered
      const offererSelect = await screen.findByLabelText('Lieu')
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, [firstVenueId])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner le lieu'
      )
      expect(offerVenueSelect).toHaveValue(firstVenueId)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      await userEvent.click(await screen.findByLabelText('Dans votre lieu'))
      expect(screen.getByLabelText('Dans votre lieu')).toBeChecked()

      expect(offerVenueSelect).toHaveValue(firstVenueId)
    })

    it('should prefill intervention field with venue intervention field when selecting venue', async () => {
      const offererId = '55'
      const venueId = '42'
      renderWithProviders(
        <OfferEducational
          {...props}
          userOfferers={[
            ...props.userOfferers,
            userOffererFactory({
              id: offererId,
              nonHumanizedId: Number(offererId),
              managedVenues: [
                managedVenueFactory({}),
                managedVenueFactory({
                  id: venueId,
                  nonHumanizedId: Number(venueId),
                  collectiveInterventionArea: ['01', '02'],
                }),
              ],
            }),
          ]}
        />
      )

      const offererSelect = await screen.findByLabelText('Structure')

      await userEvent.selectOptions(offererSelect, [offererId])
      expect(screen.queryByLabelText('Structure')).toHaveValue(offererId)

      const venuesSelect = await screen.findByLabelText('Lieu')

      await userEvent.selectOptions(venuesSelect, [venueId])

      expect(screen.queryByLabelText('Lieu')).toHaveValue(venueId)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()
      const interventionArea = await screen.findByLabelText(
        INTERVENTION_AREA_LABEL
      )
      await userEvent.click(interventionArea)
      await waitFor(() => {
        const checkboxes = screen.getAllByRole('checkbox', { checked: true })
        expect(
          checkboxes.filter(
            checkbox => checkbox.getAttribute('name') === 'interventionArea'
          )
        ).toHaveLength(2)
      })
    })
  })
})
