import type { LoaderFunctionArgs } from 'react-router'
import * as reactRouter from 'react-router'

import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import type { UserPermissions } from '../types'
import { withUserPermissions } from '../withUserPermissions'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    redirect: vi.fn((path: string) => ({ type: 'redirect', path })),
  }
})

const setupStore = (options: {
  access?: UserAccess | null
  hasUser?: boolean
  hasVenue?: boolean
  isFeatureActive?: boolean
}) => {
  const store = configureTestStore({
    features: {
      list: options.isFeatureActive
        ? [{ id: 1, isActive: true, name: 'WIP_SWITCH_VENUE' }]
        : [],
    },
    user: {
      access: options.access ?? null,
      currentUser: options.hasUser ? sharedCurrentUserFactory() : null,
      selectedVenue: options.hasVenue
        ? makeGetVenueResponseModel({ id: 1 })
        : null,
      venues: null,
    },
  })
  vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)
}

const createMockLoaderArgs = (url: string): LoaderFunctionArgs =>
  ({
    request: new Request(url),
    params: {},
  }) as LoaderFunctionArgs

describe('withUserPermissions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('without WIP_SWITCH_VENUE feature flag', () => {
    it('should execute the original loader without permission check', () => {
      setupStore({ isFeatureActive: false })
      const mockLoader = vi.fn(() => 'loader result')
      const permissionCheck = vi.fn(() => false)
      const args = createMockLoaderArgs('http://localhost/some-page')

      const guardedLoader = withUserPermissions(permissionCheck, mockLoader)
      const result = guardedLoader(args)

      expect(result).toBe('loader result')
      expect(mockLoader).toHaveBeenCalledWith(args)
      expect(permissionCheck).not.toHaveBeenCalled()
    })

    it('should return null when no loader is provided', () => {
      setupStore({ isFeatureActive: false })
      const permissionCheck = vi.fn(() => false)
      const args = createMockLoaderArgs('http://localhost/some-page')

      const guardedLoader = withUserPermissions(permissionCheck)
      const result = guardedLoader(args)

      expect(result).toBeNull()
    })
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    describe('when user is allowed', () => {
      it('should execute the original loader', () => {
        setupStore({
          isFeatureActive: true,
          hasUser: true,
          hasVenue: true,
          access: 'full',
        })
        const mockLoader = vi.fn(() => 'loader result')
        const permissionCheck = (_: UserPermissions) => true
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck, mockLoader)
        const result = guardedLoader(args)

        expect(result).toBe('loader result')
        expect(mockLoader).toHaveBeenCalledWith(args)
      })

      it('should return null when no loader is provided', () => {
        setupStore({
          isFeatureActive: true,
          hasUser: true,
          hasVenue: true,
          access: 'full',
        })
        const permissionCheck = (_: UserPermissions) => true
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        const result = guardedLoader(args)

        expect(result).toBeNull()
      })
    })

    describe('when user is not allowed', () => {
      it('should redirect to /connexion when not authenticated', () => {
        setupStore({ isFeatureActive: true, hasUser: false })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        guardedLoader(args)

        expect(reactRouter.redirect).toHaveBeenCalledWith('/connexion')
      })

      it('should redirect to /hub when authenticated but no venue selected', () => {
        setupStore({ isFeatureActive: true, hasUser: true, hasVenue: false })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        guardedLoader(args)

        expect(reactRouter.redirect).toHaveBeenCalledWith('/hub')
      })

      it('should redirect to /rattachement-en-cours when venue is unattached', () => {
        setupStore({
          isFeatureActive: true,
          hasUser: true,
          hasVenue: true,
          access: 'unattached',
        })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        guardedLoader(args)

        expect(reactRouter.redirect).toHaveBeenCalledWith(
          '/rattachement-en-cours'
        )
      })

      it('should redirect to /onboarding when user is not onboarded', () => {
        setupStore({
          isFeatureActive: true,
          hasUser: true,
          hasVenue: true,
          access: 'no-onboarding',
        })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        guardedLoader(args)

        expect(reactRouter.redirect).toHaveBeenCalledWith('/onboarding')
      })

      it('should redirect to /accueil when user has full access but is not allowed', () => {
        setupStore({
          isFeatureActive: true,
          hasUser: true,
          hasVenue: true,
          access: 'full',
        })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        guardedLoader(args)

        expect(reactRouter.redirect).toHaveBeenCalledWith('/accueil')
      })
    })
  })
})
