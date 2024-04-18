import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { UserEmailForm } from '..'
import { UserEmailFormProps } from '../UserEmailForm'

const renderUserEmailForm = (props: UserEmailFormProps) => {
  return renderWithProviders(<UserEmailForm {...props} />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('components:UserEmailForm', () => {
  let props: UserEmailFormProps
  beforeEach(() => {
    vi.spyOn(api, 'postUserEmail').mockResolvedValue()
    props = {
      closeForm: vi.fn(),
      getPendingEmailRequest: vi.fn(),
    }
  })

  it('renders component successfully', () => {
    renderUserEmailForm(props)
    expect(screen.getAllByRole('textbox').length).toBe(1)
  })

  it('should trigger onSubmit callback when submitting', async () => {
    renderUserEmailForm(props)
    await userEvent.type(
      screen.getByLabelText('Nouvelle adresse email *'),
      'test@test.com'
    )
    await userEvent.type(
      screen.getByLabelText(
        'Mot de passe (requis pour modifier votre email) *'
      ),
      'test'
    )
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))
    expect(api.postUserEmail).toHaveBeenCalledTimes(1)
  })
})
