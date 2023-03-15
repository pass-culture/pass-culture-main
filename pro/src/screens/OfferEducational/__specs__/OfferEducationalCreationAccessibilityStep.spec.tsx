import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducational from '../'
import {
  categoriesFactory,
  defaultCreationProps,
  managedVenueFactory,
  subCategoriesFactory,
} from '../__tests-utils__'
import { userOffererFactory } from '../__tests-utils__/userOfferersFactory'
import { IOfferEducationalProps } from '../OfferEducational'
describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>

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

  it('should prefill intervention and accessibility fields with venue intervention field when selecting venue', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        id: 'OFFERER_WITH_ACCESSIBILITY',
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            id: 'VENUE_WITH_ACCESSIBILITY',
            mentalDisabilityCompliant: true,
            motorDisabilityCompliant: true,
            visualDisabilityCompliant: false,
            audioDisabilityCompliant: false,
          }),
        ],
      }),
    ]
    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: store,
    })

    const offererSelect = await screen.findByLabelText('Structure')

    await userEvent.selectOptions(offererSelect, ['OFFERER_WITH_ACCESSIBILITY'])

    const venuesSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venuesSelect, ['VENUE_WITH_ACCESSIBILITY'])

    const accessibilityCheckboxes = screen.queryAllByRole('checkbox', {
      checked: true,
    })

    await waitFor(() => expect(accessibilityCheckboxes).toHaveLength(2))
  })

  it('should prefill event address venue when selecting venue for reimbursement', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        id: 'offerer',
        managedVenues: [
          managedVenueFactory({ id: 'first_venue', name: 'First venue name' }),
          managedVenueFactory({
            id: 'second_venue',
            name: 'Second venue name',
          }),
        ],
      }),
    ]
    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: store,
    })

    const offererSelect = await screen.findByLabelText('Structure')

    await userEvent.selectOptions(offererSelect, ['offerer'])

    const venuesSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venuesSelect, ['first_venue'])

    const offerVenueSelect = await screen.findByLabelText(
      'Sélectionner le lieu'
    )
    expect(offerVenueSelect).toHaveValue('first_venue')

    expect(
      screen.getByText('First venue name', { exact: false, selector: 'div' })
    ).toBeInTheDocument()

    await userEvent.selectOptions(venuesSelect, ['second_venue'])

    expect(offerVenueSelect).toHaveValue('second_venue')

    expect(
      screen.getByText('Second venue name', { exact: false, selector: 'div' })
    ).toBeInTheDocument()
  })
})
