import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'
import { beforeEach, expect } from 'vitest'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events, VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  RedirectToBankAccountDialog,
  type RedirectToBankAccountDialogProps,
} from './RedirectToBankAccountDialog'

const SELECTED_PARTNER_VENUE_ID = 10
const SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID = 1
const CANCEL_REDIRECT_URL = '/cancel-target'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))
vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
  },
}))

const renderDialog = (
  customProps: Partial<RedirectToBankAccountDialogProps> = {},
  options: RenderWithProvidersOptions = {}
) => {
  const props: RedirectToBankAccountDialogProps = {
    cancelRedirectUrl: CANCEL_REDIRECT_URL,
    isDialogOpen: true,
    ...customProps,
  }

  return renderWithProviders(<RedirectToBankAccountDialog {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        offererNames: [
          getOffererNameFactory({
            id: SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID,
            validated: true,
          }),
        ],
        selectedAdminOfferer: null,
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: SELECTED_PARTNER_VENUE_ID,
          managingOffererId: SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID,
        }),
        venues: [],
        venuesWithPendingValidation: [],
      },
    },
    initialRouterEntries: ['/accueil'],
    ...options,
  })
}

describe('<RedirectToBankAccountDialog />', () => {
  const mockLogEvent = vi.fn()
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    // Default mocks so the venue refresh path (when triggered) resolves cleanly.
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: SELECTED_PARTNER_VENUE_ID,
        managingOffererId: SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID,
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID,
    })
  })

  it('should render the dialog title and both action buttons', () => {
    renderDialog()

    expect(
      screen.getByRole('heading', { name: /Félicitations/ })
    ).toBeInTheDocument()
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('Plus tard')).toBeInTheDocument()
  })

  describe('trackers', () => {
    it('should log the "add bank account" event when the confirm button is clicked', async () => {
      renderDialog()

      await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

      expect(mockLogEvent).toHaveBeenCalledWith(
        VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON
      )
    })

    it('should log the "see later" event when the cancel button is clicked', async () => {
      renderDialog()

      await userEvent.click(screen.getByText('Plus tard'))

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL
      )
    })
  })

  describe('confirm path (Ajouter un compte bancaire)', () => {
    it('should refresh the selected partner venue and then navigate to the bank account admin page when on the onboarding flow', async () => {
      renderDialog(undefined, {
        initialRouterEntries: ['/onboarding/individuel'],
      })

      await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledExactlyOnceWith(
          '/administration/remboursements/informations-bancaires'
        )
      })
      expect(api.getVenue).toHaveBeenCalledExactlyOnceWith(
        SELECTED_PARTNER_VENUE_ID
      )
      expect(api.getOfferer).toHaveBeenCalledWith(
        SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID
      )
    })

    it('should navigate to the bank account admin page without refreshing the venue when outside the onboarding flow', async () => {
      renderDialog(undefined, { initialRouterEntries: ['/accueil'] })

      await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledExactlyOnceWith(
          '/administration/remboursements/informations-bancaires'
        )
      })
      expect(api.getVenue).not.toHaveBeenCalled()
      expect(api.getOfferer).not.toHaveBeenCalled()
    })

    it('should navigate only after the venue refresh has resolved (order guarantee)', async () => {
      renderDialog(undefined, {
        initialRouterEntries: ['/onboarding/individuel'],
      })

      await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalled()
      })
      // `mock.invocationCallOrder` exposes a monotonic global counter across all
      // vitest mocks. A smaller number means the call happened earlier.
      const getVenueOrder = vi.mocked(api.getVenue).mock.invocationCallOrder[0]
      const navigateOrder = mockNavigate.mock.invocationCallOrder[0]
      expect(getVenueOrder).toBeLessThan(navigateOrder)
    })
  })

  describe('cancel path (Plus tard)', () => {
    it('should refresh the selected partner venue and then navigate to cancelRedirectUrl when on the onboarding flow', async () => {
      renderDialog(
        { cancelRedirectUrl: '/custom-cancel' },
        { initialRouterEntries: ['/onboarding/individuel'] }
      )

      await userEvent.click(screen.getByText('Plus tard'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledExactlyOnceWith('/custom-cancel')
      })
      expect(api.getVenue).toHaveBeenCalledExactlyOnceWith(
        SELECTED_PARTNER_VENUE_ID
      )
      expect(api.getOfferer).toHaveBeenCalledWith(
        SELECTED_PARTNER_VENUE_MANAGING_OFFERER_ID
      )
    })

    it('should navigate to cancelRedirectUrl without refreshing the venue when outside the onboarding flow', async () => {
      renderDialog(
        { cancelRedirectUrl: '/custom-cancel' },
        { initialRouterEntries: ['/accueil'] }
      )

      await userEvent.click(screen.getByText('Plus tard'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledExactlyOnceWith('/custom-cancel')
      })
      expect(api.getVenue).not.toHaveBeenCalled()
      expect(api.getOfferer).not.toHaveBeenCalled()
    })

    it('should navigate only after the venue refresh has resolved (order guarantee)', async () => {
      renderDialog(undefined, {
        initialRouterEntries: ['/onboarding/individuel'],
      })

      await userEvent.click(screen.getByText('Plus tard'))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalled()
      })
      const getVenueOrder = vi.mocked(api.getVenue).mock.invocationCallOrder[0]
      const navigateOrder = mockNavigate.mock.invocationCallOrder[0]
      expect(getVenueOrder).toBeLessThan(navigateOrder)
    })
  })
})
