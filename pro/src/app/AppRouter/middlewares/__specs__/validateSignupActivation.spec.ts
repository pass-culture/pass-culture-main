import type { LoaderFunctionArgs } from 'react-router'
import * as reactRouter from 'react-router'

import { api } from '@/apiClient/api'
import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { makeApiError } from '@/commons/utils/factories/errorFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { validateSignupActivation } from '../validateSignupActivation'

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

const setupStore = (features: string[]) => {
  const store = configureTestStore({
    features: {
      list: features.map((name, index) => ({
        id: index,
        isActive: true,
        name,
      })),
    },
  })
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
    vi.clearAllMocks()
  })

  it('should return early when WIP_SWITCH_VENUE feature is not active', async () => {
    setupStore([])
    const args = createMockLoaderArgs('some-token')

    const result = await validateSignupActivation(args)

    expect(result).toBeUndefined()
    expect(api.validateUser).not.toHaveBeenCalled()
    expect(reactRouter.redirect).not.toHaveBeenCalled()
  })

  it('should redirect to /connexion when token is missing', async () => {
    setupStore(['WIP_SWITCH_VENUE'])
    const args = createMockLoaderArgs()

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).not.toHaveBeenCalled()
  })

  it('should validate user, initialize profile, show success snackbar and redirect to /connexion', async () => {
    const store = setupStore(['WIP_SWITCH_VENUE'])
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

    expect(api.validateUser).toHaveBeenCalledWith('valid-token')
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
    const store = setupStore(['WIP_SWITCH_VENUE'])
    vi.spyOn(api, 'validateUser').mockRejectedValueOnce(
      makeApiError({ body: { global: 'Token expired' } })
    )
    vi.spyOn(store, 'dispatch')
    const args = createMockLoaderArgs('expired-token')

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledWith('expired-token')
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
  })

  it('should redirect to /connexion without snackbar when a non-API error is thrown', async () => {
    const store = setupStore(['WIP_SWITCH_VENUE'])
    vi.spyOn(api, 'validateUser').mockRejectedValueOnce(
      new Error('Network error')
    )
    vi.spyOn(store, 'dispatch')
    const args = createMockLoaderArgs('some-token')

    await expect(validateSignupActivation(args)).rejects.toEqual({
      type: 'redirect',
      path: '/connexion',
    })

    expect(api.validateUser).toHaveBeenCalledWith('some-token')
    expect(api.getProfile).not.toHaveBeenCalled()
    expect(store.dispatch).not.toHaveBeenCalled()
  })
})
