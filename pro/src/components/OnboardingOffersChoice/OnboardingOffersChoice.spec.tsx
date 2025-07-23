import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach } from 'vitest'
import { axe } from 'vitest-axe'

import * as useAnalytics from 'app/App/analytics/firebase'
import { OnboardingDidacticEvents } from 'commons/core/FirebaseEvents/constants'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { OnboardingOffersChoice } from './OnboardingOffersChoice'

const mockLogEvent = vi.fn()

describe('OnboardingOffersChoice Component', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderWithProviders(<OnboardingOffersChoice />, {
      storeOverrides: {
        offerer: {
          currentOfferer: { id: 1, isOnboarded: false },
          offererNames: [],
        },
      },
    })
  })

  it('should pass axe accessibility tests', async () => {
    const { container } = renderWithProviders(<OnboardingOffersChoice />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the first card with correct title, description, and button', () => {
    // Check for the first card's title
    const firstCardTitle = screen.getByText(
      'Sur l’application mobile à destination des jeunes'
    )
    expect(firstCardTitle).toBeInTheDocument()

    // Check for the first card's button
    const firstCardButton = screen.getAllByText('Commencer')[0]
    expect(firstCardButton).toBeInTheDocument()
  })

  it('renders the second card with correct title, description, and button', () => {
    // Check for the second card's title
    const secondCardTitle = screen.getByText(
      'Sur ADAGE à destination des enseignants'
    )
    expect(secondCardTitle).toBeInTheDocument()

    // Check for the second card's button
    const secondCardButton = screen.getAllByText('Commencer')[1]
    expect(secondCardButton).toBeInTheDocument()
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
})
