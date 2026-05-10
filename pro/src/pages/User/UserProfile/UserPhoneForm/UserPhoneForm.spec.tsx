import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import { ApiError, type ApiResult } from '@/apiClient/compat'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { UserPhoneForm, type UserPhoneFormProps } from './UserPhoneForm'

const renderUserPhoneForm = (props: UserPhoneFormProps) => {
  return renderWithProviders(<UserPhoneForm {...props} />, {
    user: sharedCurrentUserFactory(),
  })
}

const INITIAL_PHONE_NUMBER = '0615142345' as const

describe('components:UserPhoneForm', () => {
  let props: UserPhoneFormProps

  beforeEach(() => {
    props = {
      closeForm: vi.fn(),
      initialValues: {
        phoneNumber: INITIAL_PHONE_NUMBER,
      },
    }
  })

  it('renders component successfully', () => {
    renderUserPhoneForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(1)
  })

  it('should render api error when submitting', async () => {
    vi.spyOn(apiNew, 'patchUserPhone').mockRejectedValue(
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
    await userEvent.type(phoneInput, '0621790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(apiNew.patchUserPhone).toHaveBeenCalledWith({
      body: {
        phoneNumber: '+330621790350',
      },
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
        screen.getByText(
          'Veuillez renseigner un numéro de téléphone valide, exemple : 6 12 34 56 78'
        )
      ).toBeInTheDocument()
    })
  })

  it('should trigger onSubmit callback when submitting', async () => {
    vi.spyOn(apiNew, 'patchUserPhone')

    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })

    await userEvent.clear(phoneInput)
    await userEvent.type(phoneInput, '0621790350')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(apiNew.patchUserPhone).toHaveBeenCalledWith({
      body: {
        phoneNumber: '+330621790350',
      },
    })
  })

  it('should reset phone number onclick "annuler', async () => {
    renderUserPhoneForm(props)

    const phoneInput = screen.getByRole('textbox', {
      name: /Numéro de téléphone/,
    })

    await userEvent.type(phoneInput, '0692790350')
    await userEvent.click(screen.getByText('Annuler'))

    expect(phoneInput).toHaveValue(INITIAL_PHONE_NUMBER)
  })
})
