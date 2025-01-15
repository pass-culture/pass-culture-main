import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from 'commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

function renderComponent(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: { selectedOffererId: 1, offererNames: [], isOnboarded: true },
    },
  })
}

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps

  const firstVenueId = 12
  const secondVenueId = 13
  const offererId = 15
  beforeEach(() => {
    props = {
      ...defaultCreationProps,
    }
  })

  it('should prefill intervention and accessibility fields with venue intervention field when selecting venue', async () => {
    props.userOfferer = userOffererFactory({
      id: offererId,
      managedVenues: [
        managedVenueFactory({}),
        managedVenueFactory({
          id: 43,
          mentalDisabilityCompliant: true,
          motorDisabilityCompliant: true,
          visualDisabilityCompliant: false,
          audioDisabilityCompliant: false,
        }),
      ],
    })
    renderComponent(props)

    const venuesSelect = await screen.findByLabelText('Lieu *')
    await userEvent.selectOptions(venuesSelect, ['43'])

    const accessibilityCheckboxes = screen.queryAllByRole('checkbox', {
      checked: true,
    })

    await waitFor(() => expect(accessibilityCheckboxes).toHaveLength(2))
  })

  it('should prefill event address venue when selecting venue for reimbursement', async () => {
    props.userOfferer = userOffererFactory({
      id: offererId,
      managedVenues: [
        managedVenueFactory({
          id: firstVenueId,
          name: 'First venue name',
        }),
        managedVenueFactory({
          id: secondVenueId,
          name: 'Second venue name',
        }),
      ],
    })

    renderComponent(props)

    const venuesSelect = await screen.findByLabelText('Lieu *')
    await userEvent.selectOptions(venuesSelect, [firstVenueId.toString()])

    const offerVenueSelect = await screen.findByLabelText(
      'Sélectionner le lieu *'
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
