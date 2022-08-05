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
} from '../__tests-utils__'
import { userOffererFactory } from '../__tests-utils__/userOfferersFactory'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>

  beforeEach(() => {
    props = {
      ...defaultCreationProps,
      educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
      educationalSubCategories: subCategoriesFactory([
        { categoryId: 'CAT_1', id: 'SUBCAT_1' },
      ]),
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
    renderEACOfferForm(props, store)

    const offererSelect = await screen.findByLabelText('Structure')

    await userEvent.selectOptions(offererSelect, ['OFFERER_WITH_ACCESSIBILITY'])

    const venuesSelect = await screen.findByLabelText(
      'Lieu qui percevra le remboursement'
    )
    await userEvent.selectOptions(venuesSelect, ['VENUE_WITH_ACCESSIBILITY'])

    const accessibilityCheckboxes = screen.queryAllByRole('checkbox', {
      checked: true,
    })

    await waitFor(() => expect(accessibilityCheckboxes).toHaveLength(2))
  })
})
