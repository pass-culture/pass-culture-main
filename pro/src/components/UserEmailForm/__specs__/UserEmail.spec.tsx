import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { UserEmailForm } from '..'
import { IUserEmailFormProps } from '../UserEmailForm'

const postEmailAdapterMock = jest.fn()

const renderUserEmailForm = (props: IUserEmailFormProps) => {
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

  return renderWithProviders(<UserEmailForm {...props} />, { storeOverrides })
}

describe('components:UserEmailForm', () => {
  let props: IUserEmailFormProps
  beforeEach(() => {
    postEmailAdapterMock.mockResolvedValue({})
    props = {
      closeForm: jest.fn(),
      postEmailAdapter: postEmailAdapterMock,
      getPendingEmailRequest: jest.fn(),
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
    await expect(postEmailAdapterMock).toHaveBeenCalledTimes(1)
  })
})
