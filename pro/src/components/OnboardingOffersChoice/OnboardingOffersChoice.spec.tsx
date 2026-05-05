import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach } from 'vitest'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { OnboardingDidacticEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OnboardingOffersChoice } from './OnboardingOffersChoice'

const mockLogEvent = vi.fn()
const mockNavigate = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: () => mockNavigate,
}))

describe('OnboardingOffersChoice Component', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderWithProviders(<OnboardingOffersChoice />, {
      storeOverrides: {
        offerer: {
          currentOfferer: { id: 1, isOnboarded: false },
          offererNamesValidated: [],
        },
      },
    })
  })

  it('should pass axe accessibility tests', async () => {
    const { container } = renderWithProviders(<OnboardingOffersChoice />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the first card with correct title, description, and button', () => {
    expect(
      screen.getByRole('heading', {
        level: 3,
        name: 'Sur l’application mobile à destination des jeunes',
      })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', {
        name: 'Commencer la création d’offre sur l’application mobile',
      })
    ).toHaveTextContent('Créer une offre individuelle')
  })

  it('renders the second card with correct title, description, and button', () => {
    expect(
      screen.getByRole('heading', {
        name: /Sur ADAGE à destination des enseignants/,
      })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', {
        name: /Commencer la création d.offre sur ADAGE/,
      })
    ).toHaveTextContent('Déposer un dossier ADAGE')
  })

  it('displays the onboarding collective modal when the second button is clicked', async () => {
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Commencer la création d’offre sur ADAGE',
      })
    )

    expect(
      await screen.findByTestId('onboarding-collective-modal')
    ).toBeInTheDocument()
  })

  describe('trackers', () => {
    it('should track choosing collective offers', async () => {
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Commencer la création d’offre sur ADAGE',
        })
      )

      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledWith(
          OnboardingDidacticEvents.HAS_CLICKED_START_COLLECTIVE_DIDACTIC_ONBOARDING
        )
      })
    })
  })

  it('should handle skip link', async () => {
    await userEvent.click(
      screen.getByRole('button', { name: 'Je le ferai plus tard' })
    )
    expect(mockNavigate).toHaveBeenCalledWith('/accueil')
  })
})
