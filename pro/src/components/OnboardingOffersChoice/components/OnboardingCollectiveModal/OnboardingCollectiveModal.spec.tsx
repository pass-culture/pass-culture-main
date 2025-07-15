import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as router from 'react-router'
import { beforeEach, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { OnboardingDidacticEvents } from 'commons/core/FirebaseEvents/constants'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OnboardingCollectiveModal } from './OnboardingCollectiveModal'

const renderOnboardingCollectiveModal = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingCollectiveModal />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: {
        currentOfferer: { id: 1, isOnboarded: false },
        offererNames: [],
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
    vi.mock('react-router', async () => ({
      ...(await vi.importActual('react-router')),
      useNavigate: vi.fn(),
    }))

    vi.mock('apiClient/api', () => ({
      api: {
        getOffererEligibility: vi.fn(),
      },
    }))

    it('should request the API when clicking on "J’ai déposé un dossier"', async () => {
      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(api.getOffererEligibility).toHaveBeenCalledOnce()
    })

    it('should redirect to the homepage if user is onboarded', async () => {
      const mockNavigate = vi.fn()
      vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
      vi.spyOn(api, 'getOffererEligibility').mockResolvedValue({
        offererId: 1,
        isOnboarded: true,
      })

      renderOnboardingCollectiveModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(mockNavigate).toHaveBeenCalledWith('/accueil')
    })

    it('should show an error message if user is not onboarded', async () => {
      vi.spyOn(api, 'getOffererEligibility').mockResolvedValue({
        offererId: 1,
        isOnboarded: false,
      })

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

    it('should show an error message if server responded with an error', async () => {
      vi.spyOn(api, 'getOffererEligibility').mockRejectedValue({})

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
