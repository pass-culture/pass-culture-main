// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import { UserPasswordForm } from '..'
import { IUserPasswordFormProps } from '../UserPasswordForm'

const postPasswordAdapterMock = jest.fn()

const renderUserPasswordForm = (props: IUserPasswordFormProps) => {
  const store = configureTestStore({
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
  })
  return render(
    <Provider store={store}>
      <UserPasswordForm {...props} />
    </Provider>
  )
}

describe('new_components:UserPasswordForm', () => {
  let props: IUserPasswordFormProps
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
