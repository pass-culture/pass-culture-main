import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import {
  managedVenueFactory,
  userOffererFactory,
  userOfferersFactory,
} from '../__tests-utils__/userOfferersFactory'
import { INTERVENTION_AREA_LABEL } from '../constants/labels'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps

  describe('when there is only one venue managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
      }
    })

    it('should display venue radio buttons with pre-selected offerer venue and a disabled select', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      expect(await screen.findByLabelText('Dans votre lieu')).toBeChecked()
      expect(
        screen.getByLabelText('Dans l’établissement scolaire')
      ).not.toBeChecked()
      expect(screen.getByLabelText('Autre')).not.toBeChecked()

      expect(screen.getByLabelText('Sélectionner le lieu *')).toHaveValue('1')
      expect(screen.getByLabelText('Sélectionner le lieu *')).toBeDisabled()

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
        screen.queryByLabelText('Sélectionner le lieu *')
      ).not.toBeInTheDocument()

      expect(
        screen.getByLabelText('Adresse de l’évènement *')
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText(`${INTERVENTION_AREA_LABEL} *`)
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
        screen.queryByLabelText('Sélectionner le lieu *')
      ).not.toBeInTheDocument()

      expect(
        screen.queryByLabelText('Adresse de l’évènement *')
      ).not.toBeInTheDocument()

      expect(
        screen.queryByLabelText(`${INTERVENTION_AREA_LABEL} *`)
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
            id: 1,
            managedVenues: [
              managedVenueFactory({
                id: Number(firstVenueId),
              }),
              managedVenueFactory({
                id: Number(secondVenueId),
              }),
            ],
          },
        ]),
      }
    })

    it('should require an offer venue selection from the user', async () => {
      renderWithProviders(<OfferEducational {...props} />)

      // wait for page to be rendered
      const offererSelect = await screen.findByLabelText('Lieu *')
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, [firstVenueId])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner le lieu *'
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
      const offererSelect = await screen.findByLabelText('Lieu *')
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, [firstVenueId])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner le lieu *'
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
              id: Number(offererId),
              managedVenues: [
                managedVenueFactory({}),
                managedVenueFactory({
                  id: Number(venueId),
                  collectiveInterventionArea: ['01', '02'],
                }),
              ],
            }),
          ]}
        />
      )

      const offererSelect = await screen.findByLabelText('Structure *')

      await userEvent.selectOptions(offererSelect, [offererId])
      expect(screen.queryByLabelText('Structure *')).toHaveValue(offererId)

      const venuesSelect = await screen.findByLabelText('Lieu *')

      await userEvent.selectOptions(venuesSelect, [venueId])

      expect(screen.queryByLabelText('Lieu *')).toHaveValue(venueId)

      await userEvent.click(await screen.findByLabelText('Autre'))

      expect(screen.getByLabelText('Autre')).toBeChecked()

      const interventionArea = await screen.findByLabelText(
        `${INTERVENTION_AREA_LABEL} *`
      )
      await userEvent.click(interventionArea)

      const interventionAreaContainer = screen.getByTestId(
        'wrapper-search-interventionArea'
      )

      const checkedItems = within(interventionAreaContainer).getAllByRole(
        'checkbox',
        { checked: true }
      )
      expect(checkedItems).toHaveLength(2)
    })
  })
})
