import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { ApiError } from '@/apiClient//adage'
import { ApiRequestOptions } from '@/apiClient//adage/core/ApiRequestOptions'
import { ApiResult } from '@/apiClient//adage/core/ApiResult'
import { api } from '@/apiClient//api'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { UserIdentityForm, UserIdentityFormProps } from '../UserIdentityForm'

const renderUserIdentityForm = (props: UserIdentityFormProps) => {
  return renderWithProviders(
    <>
      <UserIdentityForm {...props} />
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
    }
  )
}

describe('components:UserIdentityForm', () => {
  let props: UserIdentityFormProps
  beforeEach(() => {
    props = {
      closeForm: vi.fn(),
      initialValues: {
        firstName: 'FirstName',
        lastName: 'lastName',
      },
    }
    vi.spyOn(api, 'patchUserIdentity').mockResolvedValue({
      firstName: 'Jean',
      lastName: 'Dupont',
    })
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

    expect(api.patchUserIdentity).toHaveBeenCalledTimes(1)
  })

  it('should render api error when submitting', async () => {
    vi.spyOn(api, 'patchUserIdentity').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            firstName: 'oh no',
          },
        } as ApiResult,
        ''
      )
    )

    renderUserIdentityForm(props)

    await userEvent.type(screen.getByLabelText('Prénom'), 'Harry')
    await userEvent.tab()
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(screen.getByText('oh no')).toBeInTheDocument()
  })
})
