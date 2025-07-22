import { screen } from '@testing-library/react'

import * as useHasAccessToDidacticOnboarding from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { OnboardingOffersTypeChoice } from './OnboardingOffersTypeChoice'

vi.mock('commons/hooks/useHasAccessToDidacticOnboarding')
describe('OnboardingOffersChoice Component', () => {
  beforeEach(() => {
    vi.spyOn(
      useHasAccessToDidacticOnboarding,
      'useHasAccessToDidacticOnboarding'
    ).mockResolvedValue(true)
  })

  it('displays the content correctly', () => {
    renderWithProviders(<OnboardingOffersTypeChoice />)

    expect(
      screen.getByText('Bienvenue sur le pass Culture Pro !')
    ).toBeInTheDocument()

    expect(
      screen.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeInTheDocument()

    // Check that the first title is displayed
    expect(
      screen.getByText('Aux jeunes sur l’application mobile pass Culture')
    ).toBeInTheDocument()

    // Check that the second title is displayed
    expect(
      screen.getByText('Aux enseignants sur la plateforme ADAGE')
    ).toBeInTheDocument()
  })
})
