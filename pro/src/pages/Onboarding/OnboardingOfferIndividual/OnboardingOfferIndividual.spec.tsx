import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OnboardingOfferIndividual } from './OnboardingOfferIndividual'

const renderOnboardingOfferIndividual = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingOfferIndividual />, { ...options })
}

describe('<OnboardingOfferIndividual />', () => {
  it('should update offerType state when a radio button is selected', async () => {
    renderOnboardingOfferIndividual()

    const individualRadioButton = screen.getByLabelText(
      /Créer une offre manuellement/i
    )
    await userEvent.click(individualRadioButton)

    const nextStepButton = screen.getByText(/Étape suivante/i)
    expect(nextStepButton).not.toBeDisabled()
  })
})
