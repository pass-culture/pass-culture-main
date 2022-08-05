import '@testing-library/jest-dom'

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { RootState } from 'store/reducers'

import {
  categoriesFactory,
  defaultCreationProps,
  managedVenueFactory,
  renderEACOfferForm,
  subCategoriesFactory,
  userOfferersFactory,
} from '../__tests-utils__'
import { userOffererFactory } from '../__tests-utils__/userOfferersFactory'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>

  describe('when there is only one venue managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
        educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
        educationalSubCategories: subCategoriesFactory([
          { categoryId: 'CAT_1', id: 'SUBCAT_1' },
        ]),
      }
      store = {
        features: {
          initialized: true,
          list: [
            {
              nameKey: 'ENABLE_INTERVENTION_ZONE_COLLECTIVE_OFFER',
              isActive: true,
            },
          ],
        },
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

      expect(
        screen.queryByLabelText('Zones de Mobilités pour l’événement')
      ).not.toBeInTheDocument()
    })

    it('should display text area + intervention area multiselect when user selects "other"', async () => {
      renderEACOfferForm(props, store)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner le lieu')
      ).not.toBeInTheDocument()

      expect(
        screen.getByLabelText('Adresse de l’évènement')
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText('Zones de Mobilités pour l’événement')
      ).toBeInTheDocument()
    })

    it('should not display neither event venue address nor text area if user selects "school"', async () => {
      renderEACOfferForm(props, store)

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
        screen.queryByLabelText('Zones de Mobilités pour l’événement')
      ).toBeInTheDocument()
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

  it('should prefill intervention field with venue intervention field when selecting venue', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        id: 'OFFERER_WITH_INTERVENTION_AREA',
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            id: 'VENUE_WITH_INTERVENTION_AREA',
            collectiveInterventionArea: ['01', '02'],
          }),
        ],
      }),
    ]
    renderEACOfferForm(props, store)

    const offererSelect = await screen.findByLabelText('Structure')

    await userEvent.selectOptions(offererSelect, [
      'OFFERER_WITH_INTERVENTION_AREA',
    ])
    expect(screen.queryByLabelText('Structure')).toHaveValue(
      'OFFERER_WITH_INTERVENTION_AREA'
    )

    const venuesSelect = await screen.findByLabelText(
      'Lieu qui percevra le remboursement'
    )
    await userEvent.selectOptions(venuesSelect, [
      'VENUE_WITH_INTERVENTION_AREA',
    ])
    expect(
      screen.queryByLabelText('Lieu qui percevra le remboursement')
    ).toHaveValue('VENUE_WITH_INTERVENTION_AREA')

    await userEvent.click(await screen.findByLabelText('Autre'))
    expect(screen.getByLabelText('Autre')).toBeChecked()
    const interventionArea = await screen.findByLabelText(
      'Zones de Mobilités pour l’événement'
    )
    await userEvent.click(interventionArea)
    await waitFor(() =>
      expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(2)
    )
  })
})
