import { screen, waitFor } from '@testing-library/react'

import {
  CollectiveBookingStatus,
  CollectiveOfferAllowedAction,
} from '@/apiClient//v1'
import { Mode } from '@/commons/core/OfferEducational/types'
import * as hooks from '@/commons/hooks/swr/useOfferer'
import {
  getCollectiveOfferBookingFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferManagingOffererFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenuesFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

vi.mock('@/apiClient//api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))

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

describe('screens | OfferEducational : edition offerer step', () => {
  let props: OfferEducationalProps
  const thirdVenueId = 67
  const fourthVenueId = 92
  const secondOffererId = 92
  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  beforeEach(() => {
    vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
    props = defaultEditionProps
  })

  it('should enable venue select when CAN_EDIT_DETAILS action is allowed', async () => {
    props = {
      ...props,
      userOfferer: userOffererFactory({
        id: secondOffererId,
        managedVenues: managedVenuesFactory([
          { id: thirdVenueId },
          { id: fourthVenueId },
        ]),
      }),
      offer: getCollectiveOfferFactory({
        id: thirdVenueId,
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
        venue: {
          ...getCollectiveOfferVenueFactory({
            id: thirdVenueId,
            managingOfferer: getCollectiveOfferManagingOffererFactory({
              id: secondOffererId,
            }),
          }),
          id: thirdVenueId,
        },
      }),
    }

    renderComponent(props)

    const offerTypeTitle = await screen.findByRole('heading', {
      name: 'Quel est le type de votre offre ?',
    })
    expect(offerTypeTitle).toBeInTheDocument()

    const venueSelect = await screen.findByLabelText('Structure *')

    expect(venueSelect).toBeInTheDocument()
    expect(venueSelect).toHaveValue(thirdVenueId.toString())
    expect(venueSelect).not.toBeDisabled()
  })

  it('should display venue select disabled when CAN_EDIT_DETAILS action is not allowed', async () => {
    props = {
      ...props,
      userOfferer: userOffererFactory({
        id: secondOffererId,
        managedVenues: managedVenuesFactory([
          { id: thirdVenueId },
          { id: fourthVenueId },
        ]),
      }),
      offer: getCollectiveOfferFactory({
        id: thirdVenueId,
        venue: {
          ...getCollectiveOfferVenueFactory({
            managingOfferer: getCollectiveOfferManagingOffererFactory({
              id: secondOffererId,
            }),
          }),
          id: thirdVenueId,
        },
        booking: getCollectiveOfferBookingFactory({
          id: 1,
          status: CollectiveBookingStatus.USED,
        }),
      }),
    }
    renderComponent(props)

    const venueSelect = await screen.findByLabelText('Structure *')

    expect(venueSelect).toBeInTheDocument()
    expect(venueSelect).toHaveValue(thirdVenueId.toString())
    expect(venueSelect).toBeDisabled()
  })

  it('should show banner if generate from publicApi', async () => {
    props.mode = Mode.EDITION
    props.offer = getCollectiveOfferFactory({ isPublicApi: true })
    renderComponent(props)
    await waitFor(() => {
      expect(
        screen.getByText('Offre importée automatiquement')
      ).toBeInTheDocument()
    })
  })
})
