import { screen } from '@testing-library/react'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OnboardingOfferIndividualAutomatic } from './OnboardingOfferIndividualAutomatic'

const renderOnboardingOfferIndividualAutomatic = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingOfferIndividualAutomatic />, {
    ...options,
  })
}

describe('<OnboardingOfferIndividualAutomatic />', () => {
  it('should render correctly', async () => {
    renderOnboardingOfferIndividualAutomatic()

    expect(
      await screen.findByRole('heading', {
        name: /Connecter mon logiciel de gestion des stocks/,
      })
    ).toBeInTheDocument()
  })
})
