import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import type { UseCurrentUserReturn } from 'hooks/useCurrentUser'
import * as useCurrentUser from 'hooks/useCurrentUser'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import SignUpValidation from '../SignUpValidation'

vi.mock('repository/pcapi/pcapi')
vi.mock('hooks/useCurrentUser')
vi.mock('hooks/useNotification')

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
    close: vi.fn(),
    error: vi.fn(),
    pending: vi.fn(),
    information: vi.fn(),
    success: vi.fn(),
  }

  beforeEach(() => {
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
    }))
    vi.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {},
    } as UseCurrentUserReturn)
  })

  afterEach(vi.resetAllMocks)

  it('should redirect to home page if the user is logged in', async () => {
    const validateUser = vi.spyOn(api, 'validateUser')
    vi.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {
        id: 123,
      },
    } as UseCurrentUserReturn)
    // when the user is logged in and lands on signup validation page
    renderSignupValidation('/validation/AAA')

    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page
    expect(screen.getByText('Accueil')).toBeInTheDocument()
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()
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
    renderSignupValidation('/validation/AAA')

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })

  it('should verify user link is not valid and redirect to connexion even if the error is not an ApiError', async () => {
    vi.spyOn(api, 'validateUser').mockRejectedValue({ name: 'error' })
    // given the user lands on signup validation page
    renderSignupValidation('/validation/AAA')

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })
  })
})
