// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import { UserPhoneForm } from '../'
import { IUserPhoneFormProps } from '../UserPhoneForm'

const patchPhoneAdapterMock = jest.fn()

const renderUserPhoneForm = (props: IUserPhoneFormProps) => {
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
      <UserPhoneForm {...props} />
    </Provider>
  )
}

describe('new_components:UserPhoneForm', () => {
  let props: IUserPhoneFormProps
  beforeEach(() => {
    patchPhoneAdapterMock.mockResolvedValue({})
    props = {
      closeForm: jest.fn(),
      initialValues: {
        phoneNumber: '0615142345',
      },
      patchPhoneAdapter: patchPhoneAdapterMock,
    }
  })
  it('renders component successfully', () => {
    renderUserPhoneForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(1)
  })
  it('should trigger onSubmit callback when submitting', async () => {
    renderUserPhoneForm(props)
    await userEvent.clear(screen.getByLabelText('Téléphone'))
    await userEvent.type(screen.getByLabelText('Téléphone'), '0692790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    await expect(patchPhoneAdapterMock).toHaveBeenNthCalledWith(1, {
      phoneNumber: '+262692790350',
    })
  })
})
