import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  isUserPasswordError,
  UserPasswordForm,
  UserPasswordFormProps,
} from '../UserPasswordForm'

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
      screen.getByLabelText(/Confirmez votre nouveau mot de passe/)
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
      screen.getByLabelText(/Confirmez votre nouveau mot de passe/),
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

  it('should displays API fields errors', async () => {
    vi.spyOn(api, 'postChangePassword').mockRejectedValue({
      message: 'Une erreur est survenue',
      name: 'ApiError',
      status: 400,
      body: {
        oldPassword: ['Le mot de passe actuel est incorrect.'],
        newPassword: ['Le nouveau mot de passe est identique à l’ancien.'],
      },
    })

    let props: UserPasswordFormProps = {
      closeForm: vi.fn(),
    }

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
      screen.getByLabelText(/Confirmez votre nouveau mot de passe/),
      'MyNewSuper1Password,'
    )
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(
      await screen.findByText('Le mot de passe actuel est incorrect.')
    ).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Le nouveau mot de passe est identique à l’ancien.'
      )
    ).toBeInTheDocument()
  })

  describe('isUserPasswordError util', () => {
    it('should detect if the error is a UserPasswordError', () => {
      const error = {
        oldPassword: ['Old password is incorrect'],
      }
      expect(isUserPasswordError(error)).toBe(true)
    })

    it('should detect if the error is not a UserPasswordError', () => {
      const notEvenAnError = null
      expect(isUserPasswordError(notEvenAnError)).toBe(false)

      const error = {
        message: 'Internal server error',
      }
      expect(isUserPasswordError(error)).toBe(false)
    })
  })
})
