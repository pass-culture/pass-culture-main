import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from '@/apiClient/v1/core/ApiResult'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserPhoneForm, UserPhoneFormProps } from '../UserPhoneForm'

const renderUserPhoneForm = (props: UserPhoneFormProps) => {
  return renderWithProviders(<UserPhoneForm {...props} />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('components:UserPhoneForm', () => {
  let props: UserPhoneFormProps

  beforeEach(() => {
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

  it('should render api error when submitting', async () => {
    vi.spyOn(api, 'patchUserPhone').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ["There's might be an error"] }],
        } as ApiResult,
        ''
      )
    )

    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })

    await userEvent.clear(phoneInput)
    await userEvent.type(phoneInput, '0692790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(api.patchUserPhone).toHaveBeenCalledWith({
      phoneNumber: '+262692790350',
    })
  })

  it('should render the form with phone number input', () => {
    renderUserPhoneForm(props)

    const phoneInput = screen.getByText(/Téléphone/)
    const submitButton = screen.getByRole('button', { name: /Enregistrer/ })
    const cancelButton = screen.getByRole('button', { name: /Annuler/ })

    expect(phoneInput).toBeInTheDocument()
    expect(submitButton).toBeInTheDocument()
    expect(cancelButton).toBeInTheDocument()
  })

  it('should show validation error if phone number is invalid', async () => {
    const invalidPhoneNumber = '123'

    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })
    const submitButton = screen.getByRole('button', { name: /Enregistrer/ })

    await userEvent.type(phoneInput, invalidPhoneNumber)
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/Votre numéro de téléphone n’est pas valide/)
      ).toBeInTheDocument()
    })
  })

  it('should trigger onSubmit callback when submitting', async () => {
    vi.spyOn(api, 'patchUserPhone')

    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })

    await userEvent.clear(phoneInput)
    await userEvent.type(phoneInput, '0692790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(api.patchUserPhone).toHaveBeenCalledWith({
      phoneNumber: '+262692790350',
    })
  })

  it('should reset phone number onclick "annuler', async () => {
    vi.spyOn(api, 'patchUserPhone')

    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })

    await userEvent.type(phoneInput, '0692790350')
    await userEvent.click(screen.getByText('Annuler'))

    expect(phoneInput).toHaveValue('0615142345')
  })
})
