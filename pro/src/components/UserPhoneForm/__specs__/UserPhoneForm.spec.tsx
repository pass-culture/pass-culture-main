import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { UserPhoneForm } from '../'
import { UserPhoneFormProps } from '../UserPhoneForm'

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
    vi.spyOn(api, 'patchUserPhone')
    props = {
      closeForm: vi.fn(),
      initialValues: {
        phoneNumber: '0615142345',
      },
    }
  })

  it('renders component successfully', () => {
    renderUserPhoneForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(1)
  })

  it('should trigger onSubmit callback when submitting', async () => {
    renderUserPhoneForm(props)

    await userEvent.clear(screen.getByLabelText('Téléphone *'))
    await userEvent.type(screen.getByLabelText('Téléphone *'), '0692790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(api.patchUserPhone).toHaveBeenCalledWith({
      phoneNumber: '+262692790350',
    })
  })
})
