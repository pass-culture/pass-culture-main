import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { UserIdentityForm } from '../'
import { IUserIdentityFormProps } from '../UserIdentityForm'

const patchIdentityAdapterMock = jest.fn()

const renderUserIdentityForm = (props: IUserIdentityFormProps) => {
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

  return renderWithProviders(<UserIdentityForm {...props} />, {
    storeOverrides,
  })
}

describe('components:UserIdentityForm', () => {
  let props: IUserIdentityFormProps
  beforeEach(() => {
    patchIdentityAdapterMock.mockResolvedValue({})
    props = {
      closeForm: jest.fn(),
      initialValues: {
        firstName: 'FirstName',
        lastName: 'lastName',
      },
      patchIdentityAdapter: patchIdentityAdapterMock,
    }
  })
  it('renders component successfully', () => {
    renderUserIdentityForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(2)
  })
  it('should trigger onSubmit callback when submitting', async () => {
    renderUserIdentityForm(props)
    await userEvent.type(screen.getByLabelText('Prénom'), 'Harry')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    await expect(patchIdentityAdapterMock).toHaveBeenCalledTimes(1)
  })
})
