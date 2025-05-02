import { screen, waitFor } from '@testing-library/react'
import * as reactRedux from 'react-redux'
import { Route, Routes } from 'react-router'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as thunks from 'commons/store/user/thunks'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { SignupValidation } from '../SignUpValidation'

vi.mock('repository/pcapi/pcapi')
vi.mock('commons/store/user/thunks')
vi.mock('react-redux', { spy: true })

const renderSignupValidation = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <Routes>
      <Route path="/validation/:token" element={<SignupValidation />} />
      <Route path="/" element={<div>Accueil</div>} />
      <Route path="/connexion" element={<div>Connexion</div>} />
    </Routes>,
    {
      initialRouterEntries: ['/validation/AAA'],
      ...options,
    }
  )

describe('src | components | pages | Signup | validation', () => {
  it('should redirect to home page if the user is logged in', () => {
    const validateUser = vi.spyOn(api, 'validateUser')

    // when the user is logged in and lands on signup validation page
    renderSignupValidation({
      user: sharedCurrentUserFactory(),
    })

    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page
    expect(screen.getByText('Accueil')).toBeInTheDocument()
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()
    // when the user lands on signup validation page
    renderSignupValidation()
    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenCalledTimes(1)
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')
    // and he should be redirected to signin page
    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })

  it('should verify user link is not valid and redirect to connexion', async () => {
    vi.spyOn(api, 'validateUser').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['error1', 'error2'],
          },
        } as ApiResult,
        ''
      )
    )
    // given the user lands on signup validation page
    renderSignupValidation()

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })

  it('should verify user link is not valid and redirect to connexion even if the error is not an ApiError', async () => {
    vi.spyOn(api, 'validateUser').mockRejectedValue({ name: 'error' })
    // given the user lands on signup validation page
    renderSignupValidation()

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })

  describe('Signup with auto-login feature (under WIP_2025_SIGN_UP)', () => {
    it('should verify validity of passwordless login token and redirect to pro home page', async () => {
      const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()
      const user = sharedCurrentUserFactory()
      const getProfile = vi.spyOn(api, 'getProfile').mockResolvedValue(user)
      const initializeUserThunk = vi.spyOn(thunks, 'initializeUserThunk')
      const mockDispatch = vi.fn().mockImplementation(() => ({
        unwrap: () => Promise.resolve({ success: true }),
      }))
      vi.spyOn(reactRedux, 'useDispatch').mockReturnValue(mockDispatch)

      renderSignupValidation({ features: ['WIP_2025_SIGN_UP'] })

      // The validity of the token is verified
      await waitFor(() =>
        expect(validateUser).toHaveBeenCalledExactlyOnceWith('AAA')
      )

      // The user profile is fetched …
      await waitFor(() => expect(getProfile).toHaveBeenCalledOnce())

      // … and the user is initialized
      await waitFor(() =>
        expect(initializeUserThunk).toHaveBeenCalledExactlyOnceWith(user)
      )

      // The dispatch is called …
      await waitFor(() => expect(mockDispatch).toHaveBeenCalledOnce())

      // … and we should be redirected to the homepage
      await screen.findByText('Accueil')
    })
  })
})
