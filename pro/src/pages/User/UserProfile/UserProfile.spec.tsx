import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserProfile } from './UserProfile'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
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

const renderProfile = () =>
  renderWithProviders(
    <UserProfile
      userIdentityInitialValues={{
        firstName: 'Jean',
        lastName: 'Dupont',
      }}
      userPhoneInitialValues={{ phoneNumber: '0123456789' }}
      userEmailInitialValues={{ email: 'test@test.com' }}
    />,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
        },
      },
    }
  )

describe('UserProfile', () => {
  it('should display the back button and return to previous page on click', async () => {
    renderProfile()

    const retourBtn = screen.getByText('Retour')

    await userEvent.click(retourBtn)

    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })

  it('should open and close identity form when clicking modify button', async () => {
    renderProfile()

    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()

    const modifyButtons = screen.getAllByText('Modifier')

    await userEvent.click(modifyButtons[0])

    expect(screen.getByText('Fermer')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Fermer'))

    expect(modifyButtons[0]).toBeInTheDocument()
    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
  })

  it('should display pending email validation banner', async () => {
    vi.spyOn(apiNew, 'getUserEmailPendingValidation').mockResolvedValue({
      newEmail: 'newEmail@example.com',
    })

    renderProfile()

    expect(await screen.findByText(/newEmail@example.com/i)).toBeInTheDocument()
  })

  it('should not display pending email validation banner', () => {
    vi.spyOn(apiNew, 'getUserEmailPendingValidation').mockResolvedValue(
      undefined
    )

    renderProfile()

    expect(screen.queryByText(/newEmail@example.com/i)).not.toBeInTheDocument()
  })

  it('should display formatted phone number', () => {
    renderProfile()

    expect(screen.getByText('01 23 45 67 89')).toBeInTheDocument()
  })
})
