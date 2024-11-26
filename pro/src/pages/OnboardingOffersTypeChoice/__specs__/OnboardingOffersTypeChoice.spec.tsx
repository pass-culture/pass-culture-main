import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { OnboardingOffersTypeChoice } from '../OnboardingOffersTypeChoice'

describe('OnboardingOffersChoice Component', () => {
  it('displays the content correctly', () => {
    renderWithProviders(<OnboardingOffersTypeChoice />)

    expect(
      screen.getByText('Bienvenue sur le pass Culture Pro !')
    ).toBeInTheDocument()

    expect(
      screen.getByText('À qui souhaitez-vous proposer votre première offre ?')
    ).toBeInTheDocument()

    // Check that the first title is displayed
    expect(
      screen.getByText('Aux jeunes sur l’application mobile pass Culture')
    ).toBeInTheDocument()

    // Check that the second title is displayed
    expect(
      screen.getByText('Aux enseignants sur la plateforme ADAGE')
    ).toBeInTheDocument()

    // Check that the "plus tard" link is displayed
    expect(screen.getByText('Plus tard')).toBeInTheDocument()
  })
})
