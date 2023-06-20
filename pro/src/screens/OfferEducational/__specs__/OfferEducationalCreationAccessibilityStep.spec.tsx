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
import { OfferEducationalProps } from '../OfferEducational'
describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps
  let store: Partial<RootState>

  const firstVenueId = 12
  const secondVenueId = 13
  const offererId = 15
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
        nonHumanizedId: offererId,
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            id: '43',
            nonHumanizedId: 43,
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

    await userEvent.selectOptions(offererSelect, [offererId.toString()])

    const venuesSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venuesSelect, ['43'])

    const accessibilityCheckboxes = screen.queryAllByRole('checkbox', {
      checked: true,
    })

    await waitFor(() => expect(accessibilityCheckboxes).toHaveLength(2))
  })

  it('should prefill event address venue when selecting venue for reimbursement', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        nonHumanizedId: offererId,
        managedVenues: [
          managedVenueFactory({
            id: firstVenueId.toString(),
            nonHumanizedId: firstVenueId,
            name: 'First venue name',
          }),
          managedVenueFactory({
            id: secondVenueId.toString(),
            nonHumanizedId: secondVenueId,
            name: 'Second venue name',
          }),
        ],
      }),
    ]
    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: store,
    })

    const offererSelect = await screen.findByLabelText('Structure')

    await userEvent.selectOptions(offererSelect, [offererId.toString()])

    const venuesSelect = await screen.findByLabelText('Lieu')
    await userEvent.selectOptions(venuesSelect, [firstVenueId.toString()])

    const offerVenueSelect = await screen.findByLabelText(
      'Sélectionner le lieu'
    )
    expect(offerVenueSelect).toHaveValue(firstVenueId.toString())

    expect(
      screen.getByText('First venue name', { exact: false, selector: 'div' })
    ).toBeInTheDocument()

    await userEvent.selectOptions(venuesSelect, [secondVenueId.toString()])

    expect(offerVenueSelect).toHaveValue(secondVenueId.toString())

    expect(
      screen.getByText('Second venue name', { exact: false, selector: 'div' })
    ).toBeInTheDocument()
  })
})
