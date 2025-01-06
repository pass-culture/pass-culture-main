import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { UserPasswordForm, UserPasswordFormProps } from '../UserPasswordForm'

const renderUserPasswordForm = (props: UserPasswordFormProps) => {
  return renderWithProviders(<UserPasswordForm {...props} />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('components:UserPasswordForm', () => {
  let props: UserPasswordFormProps
  beforeEach(() => {
    vi.spyOn(api, 'postChangePassword').mockResolvedValue()
    props = {
      closeForm: vi.fn(),
    }
  })

  it('renders component successfully', () => {
    renderUserPasswordForm(props)

    expect(screen.getByLabelText(/Mot de passe actuel/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Nouveau mot de passe/)).toBeInTheDocument()
    expect(
      screen.getByLabelText(/Confirmer votre nouveau mot de passe/)
    ).toBeInTheDocument()
  })

  it('should trigger onSubmit callback when submitting', async () => {
    renderUserPasswordForm(props)

    await userEvent.type(
      screen.getByLabelText(/Mot de passe actuel/),
      'MyCurrentSuper1Password,'
    )
    await userEvent.type(
      screen.getByLabelText(/Nouveau mot de passe/),
      'MyNewSuper1Password,'
    )
    await userEvent.type(
      screen.getByLabelText(/Confirmer votre nouveau mot de passe/),
      'MyNewSuper1Password,'
    )
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    expect(api.postChangePassword).toHaveBeenNthCalledWith(1, {
      newConfirmationPassword: 'MyNewSuper1Password,',
      newPassword: 'MyNewSuper1Password,',
      oldPassword: 'MyCurrentSuper1Password,',
    })
  })
})
