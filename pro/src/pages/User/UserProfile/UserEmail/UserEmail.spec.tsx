import { api } from 'apiClient/api'
import { render, screen } from '@testing-library/react'

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
        'Pour valider ce changement, un lien de confirmation valable 24 heures vous a été envoyé à l’adresse :'
      )
    ).toBeInTheDocument()
  })
})
