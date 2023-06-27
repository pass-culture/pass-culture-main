import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { UserPasswordForm } from '..'
import { UserPasswordFormProps } from '../UserPasswordForm'

const postPasswordAdapterMock = jest.fn()

const renderUserPasswordForm = (props: UserPasswordFormProps) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        email: 'test@test.test',
        id: '11',
        isAdmin: false,
        firstName: 'John',
        lastName: 'Do',
      },
    },
  }

  return renderWithProviders(<UserPasswordForm {...props} />, {
    storeOverrides,
  })
}

describe('components:UserPasswordForm', () => {
  let props: UserPasswordFormProps
  beforeEach(() => {
    postPasswordAdapterMock.mockResolvedValue({})
    props = {
      closeForm: jest.fn(),
      postPasswordAdapter: postPasswordAdapterMock,
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
    await expect(postPasswordAdapterMock).toHaveBeenNthCalledWith(1, {
      newConfirmationPassword: 'MyNewSuper1Password,',
      newPassword: 'MyNewSuper1Password,',
      oldPassword: 'MyCurrentSuper1Password,',
    })
  })
})
