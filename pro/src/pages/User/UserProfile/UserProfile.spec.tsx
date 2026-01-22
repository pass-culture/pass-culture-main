import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserProfile } from './UserProfile'

vi.mock('@/apiClient/api', () => ({
  api: {
    anonymize: vi.fn(),
    getUserEmailPendingValidation: vi.fn(),
  },
}))

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

vi.spyOn(api, 'getUserEmailPendingValidation').mockResolvedValue({
  newEmail: 'newEmail@example.com',
})

describe('UserProfile', () => {
  it('should display the back button and return to previous page on click', async () => {
    renderWithProviders(
      <UserProfile
        userIdentityInitialValues={{ firstName: 'Jean', lastName: 'Dupont' }}
        userPhoneInitialValues={{ phoneNumber: '000' }}
        userEmailInitialValues={{ email: 'test@test' }}
      />
    )

    const retourBtn = screen.getByText('Retour')
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })
})
