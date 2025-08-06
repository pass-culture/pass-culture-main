import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as hooks from '@/commons/hooks/swr/useOfferer'
import {
  defaultGetOffererResponseModel,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

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
      offerer: currentOffererFactory(),
    },
  })
}

describe('screens | OfferEducational : accessibility step', () => {
  let props: OfferEducationalProps

  const firstVenueId = 12
  const secondVenueId = 13
  const offererId = 15

  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }
  beforeEach(() => {
    props = {
      ...defaultCreationProps,
    }

    vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        venueListItemFactory({ id: firstVenueId }),
        venueListItemFactory({ id: secondVenueId }),
      ],
    })
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

    const venuesSelect = await screen.findByLabelText('Structure *')
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

    const venuesSelect = await screen.findByLabelText('Structure *')
    await userEvent.selectOptions(venuesSelect, [firstVenueId.toString()])

    const offerVenueSelect = await screen.findByLabelText(
      'Sélectionner la structure *'
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
