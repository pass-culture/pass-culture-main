import type { LoaderFunctionArgs } from 'react-router'

import { api } from '@/apiClient/api'
import * as handleUnexpectedErrorModule from '@/commons/errors/handleUnexpectedError'
import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { makeApiError } from '@/commons/utils/factories/errorFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import {
  __resetConsumedTokenCallsForTests,
  validateSignupActivation,
} from '../validateSignupActivation'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    redirect: vi.fn((path: string) => ({ type: 'redirect', path })),
  }
})
vi.mock('@/apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    validateUser: vi.fn(),
  },
}))
vi.mock('@/commons/store/user/dispatchers/initializeUser', () => ({
  initializeUser: vi.fn((user: unknown) => ({
    type: 'user/initializeUser',
    payload: user,
    unwrap: vi.fn(),
  })),
}))

const setupStore = () => {
  const store = configureTestStore()
  vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

  return store
}

const createMockLoaderArgs = (
  token?: string
): LoaderFunctionArgs<{ token: string }> =>
  ({
    request: new Request('http://localhost/inscription/compte/confirmation'),
    params: token ? { token } : {},
  }) as unknown as LoaderFunctionArgs<{ token: string }>

describe('validateSignupActivation', () => {
  beforeEach(() => {
    __resetConsumedTokenCallsForTests()
  })

  it('should redirect to /connexion when token is missing', async () => {
    setupStore()
    const args = createMockLoaderArgs()

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).not.toHaveBeenCalled()
  })

  it('should validate user, initialize profile, show success snackbar and redirect to /connexion', async () => {
    const store = setupStore()
    const mockUser = sharedCurrentUserFactory()
    vi.spyOn(api, 'validateUser').mockResolvedValueOnce(undefined)
    vi.spyOn(api, 'getProfile').mockResolvedValueOnce(mockUser)
    vi.spyOn(store, 'dispatch').mockReturnValue({
      unwrap: vi.fn().mockResolvedValueOnce(undefined),
    } as unknown as ReturnType<typeof store.dispatch>)
    const args = createMockLoaderArgs('valid-token')

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledWith({
      path: { token: 'valid-token' },
    })
    expect(api.getProfile).toHaveBeenCalled()
    expect(store.dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'snackBar/addSnackBar',
        payload: expect.objectContaining({
          description:
            'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.',
          variant: SnackBarVariant.SUCCESS,
        }),
      })
    )
  })

  it('should show error snackbar and redirect to /connexion when API returns an error', async () => {
    const handleUnexpectedErrorSpy = vi
      .spyOn(handleUnexpectedErrorModule, 'handleUnexpectedError')
      .mockImplementation(vi.fn())
    const store = setupStore()
    vi.spyOn(api, 'validateUser').mockRejectedValueOnce(
      makeApiError({ body: { global: 'Token expired' } })
    )
    vi.spyOn(store, 'dispatch')
    const args = createMockLoaderArgs('expired-token')

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledWith({
      path: { token: 'expired-token' },
    })
    expect(api.getProfile).not.toHaveBeenCalled()
    expect(store.dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'snackBar/addSnackBar',
        payload: expect.objectContaining({
          description: 'Token expired',
          variant: SnackBarVariant.ERROR,
        }),
      })
    )
    expect(handleUnexpectedErrorSpy).not.toHaveBeenCalled()
  })

  it('should redirect to /connexion without snackbar when a non-API error is thrown', async () => {
    const handleUnexpectedErrorSpy = vi
      .spyOn(handleUnexpectedErrorModule, 'handleUnexpectedError')
      .mockImplementation(vi.fn())
    const store = setupStore()
    vi.spyOn(api, 'validateUser').mockRejectedValueOnce(
      new Error('Network error')
    )
    vi.spyOn(store, 'dispatch')

    const args = createMockLoaderArgs('some-token')

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledWith({
      path: { token: 'some-token' },
    })
    expect(api.getProfile).not.toHaveBeenCalled()
    expect(store.dispatch).not.toHaveBeenCalled()
    expect(handleUnexpectedErrorSpy).toHaveBeenCalledExactlyOnceWith(
      new Error('Network error'),
      { isSilent: true }
    )
  })

  it('should call the backend only once when invoked twice with the same token (StrictMode safeguard)', async () => {
    const handleUnexpectedErrorSpy = vi
      .spyOn(handleUnexpectedErrorModule, 'handleUnexpectedError')
      .mockImplementation(vi.fn())
    const store = setupStore()
    const mockUser = sharedCurrentUserFactory()
    vi.spyOn(api, 'validateUser').mockResolvedValue(undefined)
    vi.spyOn(api, 'getProfile').mockResolvedValue(mockUser)
    vi.spyOn(store, 'dispatch').mockReturnValue({
      unwrap: vi.fn().mockResolvedValue(undefined),
    } as unknown as ReturnType<typeof store.dispatch>)
    const args = createMockLoaderArgs('reused-token')

    const [firstCall, secondCall] = [
      validateSignupActivation(args),
      validateSignupActivation(args),
    ]

    await expect(firstCall).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })
    await expect(secondCall).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledTimes(1)
    expect(api.getProfile).toHaveBeenCalledTimes(1)
    expect(handleUnexpectedErrorSpy).not.toHaveBeenCalled()
  })
})
