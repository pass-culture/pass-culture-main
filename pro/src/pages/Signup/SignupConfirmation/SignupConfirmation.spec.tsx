import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SignupConfirmation } from 'pages/Signup/SignupConfirmation/SignupConfirmation'
import { expect } from 'vitest'
import { screen } from '@testing-library/react'

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
      screen.getByText('Cliquez sur le lien envoyé par email')
    ).toBeInTheDocument()
  })
})
