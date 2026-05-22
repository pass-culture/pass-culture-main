import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as router from 'react-router'
import { beforeEach, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { api, apiNew } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as getUserDefaultPathModule from '@/app/AppRouter/utils/getUserDefaultPath'
import { OnboardingDidacticEvents } from '@/commons/core/FirebaseEvents/constants'
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

import { OnboardingCollectiveModal } from './OnboardingCollectiveModal'

const SELECTED_VENUE_ID = 10
const SELECTED_OFFERER_ID = 1

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
  },
  apiNew: {
    synchronizeOffererOnboarding: vi.fn(),
  },
}))

const renderOnboardingCollectiveModal = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingCollectiveModal />, {
    storeOverrides: {
      user: {
        access: null,
        currentUser: sharedCurrentUserFactory(),
        offererNames: [getOffererNameFactory({ id: SELECTED_OFFERER_ID })],
        offererNamesValidated: [
          getOffererNameFactory({ id: SELECTED_OFFERER_ID }),
        ],
        offerersNamesWithPendingValidation: [],
        selectedAdminOfferer: null,
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: SELECTED_VENUE_ID,
          managingOffererId: SELECTED_OFFERER_ID,
        }),
        venues: [],
        venuesWithPendingValidation: [],
      },
    },
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

const mockLogEvent = vi.fn()

describe('<OnboardingCollectiveModal />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    // Default mocks so the synchronization + venue refresh succeed by default.
    // Individual tests override `isOnboarded` to exercise specific branches.
    vi.spyOn(apiNew, 'synchronizeOffererOnboarding').mockResolvedValue(
      undefined as never
    )
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: SELECTED_VENUE_ID,
        managingOffererId: SELECTED_OFFERER_ID,
        isOnboarded: false,
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: SELECTED_OFFERER_ID,
      isOnboarded: false,
    })
  })

  it('should render correctly', async () => {
    renderOnboardingCollectiveModal()

    expect(
      await screen.findByRole('heading', { name: /Quelles sont les étapes ?/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('link', { name: /Déposer un dossier/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderOnboardingCollectiveModal()

    expect(await axe(container)).toHaveNoViolations()
  })

  describe('API calls', () => {
    it('should trigger the synchronization endpoint when clicking on "J’ai déposé un dossier"', async () => {
      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(
        apiNew.synchronizeOffererOnboarding
      ).toHaveBeenCalledExactlyOnceWith({
        path: { offerer_id: SELECTED_OFFERER_ID },
      })
    })

    it('should redirect to the user default path if the venue refresh reports the offerer as onboarded', async () => {
      const mockNavigate = vi.fn()
      vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
      vi.spyOn(getUserDefaultPathModule, 'getUserDefaultPath').mockReturnValue(
        '/accueil'
      )
      vi.spyOn(api, 'getVenue').mockResolvedValue(
        makeGetVenueResponseModel({
          id: SELECTED_VENUE_ID,
          managingOffererId: SELECTED_OFFERER_ID,
          isOnboarded: true,
        })
      )

      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(mockNavigate).toHaveBeenCalledExactlyOnceWith('/accueil')
    })

    it('should show a specific error message if the venue refresh still reports the offerer as not onboarded', async () => {
      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(
        await screen.findByText(
          'Aucun dossier n’a été déposé par votre structure.'
        )
      ).toBeInTheDocument()
    })

    it('should show a generic error message if the synchronization endpoint fails', async () => {
      vi.spyOn(apiNew, 'synchronizeOffererOnboarding').mockRejectedValue({})

      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(
        await screen.findByText('Un problème est survenu, veuillez réessayer.')
      ).toBeInTheDocument()
    })
  })

  describe('trackers', () => {
    it('should track submitting a case', async () => {
      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('link', { name: /Déposer un dossier/ })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        OnboardingDidacticEvents.HAS_CLICKED_SUBMIT_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
      )
    })

    it('should track already submitted a case', async () => {
      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        OnboardingDidacticEvents.HAS_CLICKED_ALREADY_SUBMITTED_COLLECTIVE_CASE_DIDACTIC_ONBOARDING
      )
    })
  })
})
