import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from 'apiClient/api'
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

vi.mock('apiClient/api', () => ({
  api: {
    listOffers: vi.fn(),
  },
}))

describe('<OnboardingOfferIndividual />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOffers').mockResolvedValue([])
  })

  it('should render correctly', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      await screen.findByRole('heading', {
        name: /Offre à destination des jeunes/,
      })
    ).toBeInTheDocument()
  })

  it('should update offerType state when a radio button is selected', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const individualRadioButton = screen.getByLabelText(
      /Créer une offre manuellement/i
    )
    await userEvent.click(individualRadioButton)

    const nextStepButton = screen.getByText(/Étape suivante/i)
    expect(nextStepButton).not.toBeDisabled()
  })
})
