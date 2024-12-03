import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { OnboardingOffersChoice } from '../OnboardingOffersChoice'

describe('OnboardingOffersChoice Component', () => {
  beforeEach(() => {
    render(<OnboardingOffersChoice />)
  })

  it('should pass axe accessibility tests', async () => {
    const { container } = render(<OnboardingOffersChoice />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the first card with correct title, description, and button', () => {
    // Check for the first card's title
    const firstCardTitle = screen.getByText(
      'Aux jeunes sur l’application mobile pass Culture'
    )
    expect(firstCardTitle).toBeInTheDocument()

    // Check for the first card's button
    const firstCardButton = screen.getAllByText('Commencer')[0]
    expect(firstCardButton).toBeInTheDocument()
  })

  it('renders the second card with correct title, description, and button', () => {
    // Check for the second card's title
    const secondCardTitle = screen.getByText(
      'Aux enseignants sur la plateforme ADAGE'
    )
    expect(secondCardTitle).toBeInTheDocument()

    // Check for the second card's button
    const secondCardButton = screen.getAllByText('Commencer')[1]
    expect(secondCardButton).toBeInTheDocument()
  })
})
