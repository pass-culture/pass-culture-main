import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SignupConfirmation } from '@/pages/Signup/SignupConfirmation/SignupConfirmation'

vi.mock('@/apiClient//api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getSirenInfo: vi.fn(),
  },
}))

const renderSignup = () => renderWithProviders(<SignupConfirmation />)

describe('SignupConfirmation', () => {
  it('Should render correctly', () => {
    renderSignup()
    expect(
      screen.getByText('Cliquez sur le lien envoyé par email')
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Vous n’avez pas reçu d’email ?/)
    ).toBeInTheDocument()
  })
})
