import { screen } from '@testing-library/react'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { OnboardingOfferIndividualManual } from './OnboardingOfferIndividualManual'

const renderOnboardingOfferIndividualManual = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingOfferIndividualManual />, {
    ...options,
  })
}

describe('<OnboardingOfferIndividualManual />', () => {
  it('should render correctly', async () => {
    renderOnboardingOfferIndividualManual()

    expect(
      await screen.findByRole('heading', {
        name: /Offre à destination des jeunes/,
      })
    ).toBeInTheDocument()
  })
})
