import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { SignupValidation } from '../SignUpValidation'

vi.mock('repository/pcapi/pcapi')

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

  it('should verify validity of passwordless login token and redirect to pro home page', async () => {
    const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()
    renderSignupValidation({features: ['WIP_2025_SIGN_UP']})
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')
    await waitFor(() => {
      expect(window.location.pathname.includes("acceuil"))
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
})
