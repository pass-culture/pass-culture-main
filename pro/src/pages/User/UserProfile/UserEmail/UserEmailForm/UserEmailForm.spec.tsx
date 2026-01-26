import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserEmailForm, type UserEmailFormProps } from './UserEmailForm'

const renderUserEmailForm = (props: UserEmailFormProps) => {
  return renderWithProviders(<UserEmailForm {...props} />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('components:UserEmailForm', () => {
  let props: UserEmailFormProps
  beforeEach(() => {
    vi.spyOn(api, 'postUserEmail').mockResolvedValue()
    props = {
      closeForm: vi.fn(),
      getPendingEmailRequest: vi.fn(),
    }
  })

  it('renders component successfully', () => {
    renderUserEmailForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(1)
  })

  it('should trigger onSubmit callback when submitting', async () => {
    renderUserEmailForm(props)
    await userEvent.type(
      screen.getByLabelText('Nouvelle adresse email'),
      'test@test.com'
    )
    await userEvent.type(
      screen.getByLabelText('Mot de passe (requis pour modifier votre email)'),
      'test'
    )
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    expect(api.postUserEmail).toHaveBeenCalledTimes(1)
  })

  it('should display a custom error from api if the email could not be sent', async () => {
    vi.spyOn(api, 'postUserEmail').mockRejectedValueOnce({
      message: 'error message',
      body: { email: 'wrong email address' },
      name: 'ApiError',
    })
    renderUserEmailForm(props)

    await userEvent.type(
      screen.getByLabelText('Nouvelle adresse email'),
      'test@test.com'
    )
    await userEvent.type(
      screen.getByLabelText('Mot de passe (requis pour modifier votre email)'),
      'test'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(screen.getByText('wrong email address')).toBeInTheDocument()
  })

  it('should reset the form when clicking on cancel', async () => {
    renderUserEmailForm(props)

    await userEvent.type(
      screen.getByLabelText('Nouvelle adresse email'),
      'test@test.com'
    )
    await userEvent.type(
      screen.getByLabelText('Mot de passe (requis pour modifier votre email)'),
      'test'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(screen.getByLabelText('Nouvelle adresse email')).toHaveValue('')
    expect(
      screen.getByLabelText('Mot de passe (requis pour modifier votre email)')
    ).toHaveValue('')
  })
})
