import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { UserPhoneForm } from '../'
import { UserPhoneFormProps } from '../UserPhoneForm'

const patchPhoneAdapterMock = vi.fn()

const renderUserPhoneForm = (props: UserPhoneFormProps) => {
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

  return renderWithProviders(<UserPhoneForm {...props} />, { storeOverrides })
}

describe('components:UserPhoneForm', () => {
  let props: UserPhoneFormProps
  beforeEach(() => {
    patchPhoneAdapterMock.mockResolvedValue({})
    props = {
      closeForm: vi.fn(),
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
