import { render, screen } from '@testing-library/react'

import { api } from '@/apiClient/api'

import { UserEmail } from './UserEmail'

describe('UserEmail', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getUserEmailPendingValidation').mockResolvedValue({
      newEmail: 'newEmail@example.com',
    })
  })
  it('should display an info banner if the email is pending', async () => {
    render(
      <UserEmail
        showForm={false}
        initialValues={{ email: '' }}
        setCurrentForm={() => {}}
      />
    )

    expect(
      await screen.findByText(
        'Un lien de confirmation valable 24h a été envoyé à l’adresse :'
      )
    ).toBeInTheDocument()
  })
})
