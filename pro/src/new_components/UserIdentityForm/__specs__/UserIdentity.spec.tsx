// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'
import { Banner } from 'ui-kit'

import { UserIdentityForm } from '../'
import { IUserIdentityFormProps } from '../UserIdentityForm'

const patchIdentityAdapterMock = jest.fn()

const renderUserIdentityForm = (props: IUserIdentityFormProps) => {
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
      <UserIdentityForm {...props} />
    </Provider>
  )
}

describe('new_components:UserIdentityForm', () => {
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
