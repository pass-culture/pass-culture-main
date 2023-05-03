import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import type { IUseCurrentUserReturn } from 'hooks/useCurrentUser'
import * as useCurrentUser from 'hooks/useCurrentUser'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignUpValidation from '../SignUpValidation'

jest.mock('repository/pcapi/pcapi')
jest.mock('hooks/useCurrentUser')
jest.mock('hooks/useNotification')

const renderSignupValidation = (url: string) =>
  renderWithProviders(
    <Routes>
      <Route path="/validation/:token" element={<SignUpValidation />} />
      <Route path="/" element={<div>Accueil</div>} />
      <Route path="/connexion" element={<div>Connexion</div>} />
    </Routes>,
    {
      initialRouterEntries: [url],
    }
  )

describe('src | components | pages | Signup | validation', () => {
  const mockUseNotification = {
    close: jest.fn(),
    error: jest.fn(),
    pending: jest.fn(),
    information: jest.fn(),
    success: jest.fn(),
  }

  beforeEach(() => {
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
    }))
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {},
    } as IUseCurrentUserReturn)
  })

  afterEach(jest.resetAllMocks)

  it('should redirect to home page if the user is logged in', async () => {
    const validateUser = jest.spyOn(api, 'validateUser')
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {
        id: '123',
      },
    } as IUseCurrentUserReturn)
    // when the user is logged in and lands on signup validation page
    renderSignupValidation('/validation/AAA')

    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page
    expect(screen.getByText('Accueil')).toBeInTheDocument()
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = jest.spyOn(api, 'validateUser').mockResolvedValue()
    // when the user lands on signup validation page
    renderSignupValidation('/validation/AAA')
    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenCalledTimes(1)
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')
    // and he should be redirected to signin page
    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })

  it('should display a success message when token verification is successful', async () => {
    jest.spyOn(api, 'validateUser').mockResolvedValue()
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      success: notifySuccess,
    }))
    // given the user lands on signup validation page
    renderSignupValidation('/validation/AAA')

    // when his token is successfully validated
    // then a success message should be dispatched
    await waitFor(() => {
      expect(notifySuccess).toHaveBeenNthCalledWith(
        1,
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
    })
    expect(screen.getByText('Connexion')).toBeInTheDocument()
  })

  it('should display an error message when token verification is not successful', async () => {
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      error: notifyError,
    }))
    jest.spyOn(api, 'validateUser').mockRejectedValue(
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
    renderSignupValidation('/validation/AAA')
    // when his token is not successfully validated
    // then an error message should be dispatched
    await waitFor(() => {
      expect(notifyError).toHaveBeenNthCalledWith(1, ['error1', 'error2'])
    })
  })
})
