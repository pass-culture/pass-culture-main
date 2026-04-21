import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OnboardingOffersTypeChoice } from './OnboardingOffersTypeChoice'

describe('OnboardingOffersChoice Component', () => {
  beforeEach(() => {})

  it('displays the content correctly', () => {
    renderWithProviders(<OnboardingOffersTypeChoice />)

    expect(
      screen.getByText('Bienvenue sur pass Culture Pro !')
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        /Notre équipe vous contactera par email pour vous demander vos justificatifs d’inscription./
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/Pensez à vérifier vos spams./)).toBeInTheDocument()

    expect(
      screen.getByText('Où souhaitez-vous diffuser votre première offre ?')
    ).toBeInTheDocument()

    // Check that the first title is displayed
    expect(
      screen.getByText('Sur l’application mobile à destination des jeunes')
    ).toBeInTheDocument()

    // Check that the second title is displayed
    expect(
      screen.getByText('Sur ADAGE à destination des enseignants')
    ).toBeInTheDocument()
  })
})
