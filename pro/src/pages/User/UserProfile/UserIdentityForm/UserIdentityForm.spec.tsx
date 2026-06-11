import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  UserIdentityForm,
  type UserIdentityFormProps,
} from './UserIdentityForm'

const renderUserIdentityForm = (props: UserIdentityFormProps) => {
  return renderWithProviders(
    <>
      <UserIdentityForm {...props} />
      <SnackBarContainer />
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
    vi.spyOn(apiNew, 'patchUserIdentity').mockResolvedValue({
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

    expect(apiNew.patchUserIdentity).toHaveBeenCalledTimes(1)
  })

  it('should render api error when submitting', async () => {
    vi.spyOn(apiNew, 'patchUserIdentity').mockRejectedValueOnce(
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
