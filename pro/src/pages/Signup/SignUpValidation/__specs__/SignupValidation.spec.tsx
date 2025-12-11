import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as initializeUserModule from '@/commons/store/user/dispatchers/initializeUser'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { SignupValidation } from '../SignUpValidation'

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    getVenues: vi.fn(),
    signout: vi.fn(),
    validateUser: vi.fn(),
    getProfile: vi.fn(),
  },
}))

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

describe('SignupValidation', () => {
  const windowLocationReloadSpy = vi.fn()
  beforeEach(() => {
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      reload: windowLocationReloadSpy,
    })
    vi.spyOn(api, 'signout').mockResolvedValue()

    // because we directly use fetch in logout
    fetchMock.mockResponse((req) => {
      if (req.url.includes('/users/signout') && req.method === 'GET') {
        return { status: 200, body: JSON.stringify({ success: true }) }
      }
      return { status: 404 }
    })
  })

  it('should redirect to home page if the user is logged in', () => {
    const validateUser = vi.spyOn(api, 'validateUser')

    // when the user is logged in and lands on signup validation page
    renderSignupValidation({
      user: sharedCurrentUserFactory(),
    })

    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    expect(windowLocationReloadSpy).not.toHaveBeenCalled()

    // and he should be redirected to home page
    expect(screen.getByText('Accueil')).toBeInTheDocument()
  })

  it('should verify validity of user token and redirect to home', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'getProfile').mockResolvedValue(sharedCurrentUserFactory())

    const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()

    // when the user lands on signup validation page
    renderSignupValidation()

    await waitFor(() => {
      expect(validateUser).toHaveBeenCalledTimes(1)
    })

    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')

    // and he should be redirected to home page
    await waitFor(() => {
      expect(screen.getByText('Accueil')).toBeInTheDocument()
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

    expect(windowLocationReloadSpy).not.toHaveBeenCalled()
  })

  it('should verify user link is not valid and redirect to connexion even if the error is not an ApiError', async () => {
    vi.spyOn(api, 'validateUser').mockRejectedValue({ name: 'error' })
    // given the user lands on signup validation page
    renderSignupValidation()

    await waitFor(() => {
      expect(screen.getByText('Connexion')).toBeInTheDocument()
    })

    expect(windowLocationReloadSpy).not.toHaveBeenCalled()
  })

  it('should verify validity of passwordless login token and redirect to pro home page', async () => {
    const validateUser = vi.spyOn(api, 'validateUser').mockResolvedValue()
    const user = sharedCurrentUserFactory()
    const getProfile = vi.spyOn(api, 'getProfile').mockResolvedValue(user)
    const initializeUser = vi.spyOn(initializeUserModule, 'initializeUser')
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })

    renderSignupValidation()

    // The validity of the token is verified
    await waitFor(() =>
      expect(validateUser).toHaveBeenCalledExactlyOnceWith('AAA')
    )

    // The user profile is fetched …
    await waitFor(() => expect(getProfile).toHaveBeenCalledOnce())

    // … and the user is initialized
    await waitFor(() =>
      expect(initializeUser).toHaveBeenCalledExactlyOnceWith(user)
    )

    // … and we should be redirected to the homepage
    await screen.findByText('Accueil')
  })
})
