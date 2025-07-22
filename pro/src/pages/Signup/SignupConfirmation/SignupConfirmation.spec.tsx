import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SignupConfirmation } from 'pages/Signup/SignupConfirmation/SignupConfirmation'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getSirenInfo: vi.fn(),
  },
}))

const renderSignup = (features: string[] = []) =>
  renderWithProviders(<SignupConfirmation />, {
    features,
  })

describe('SignupConfirmation', () => {
  it('Should render correctly', () => {
    renderSignup()
    expect(
      screen.getByText(/Vous allez recevoir un lien de confirmation par email/)
    ).toBeInTheDocument()
  })
  it('Should render correctly with new signup FF', () => {
    renderSignup(['WIP_2025_SIGN_UP'])
    expect(
      screen.getByText(
        'Cliquez sur le lien que nous vous avons envoyé par email'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Vous n’avez pas reçu notre email ?/)
    ).toBeInTheDocument()
  })
})
