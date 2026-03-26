import type { LoaderFunctionArgs } from 'react-router'
import * as reactRouter from 'react-router'

import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

import type { UserPermissions } from '../types'
import { withUserPermissions } from '../withUserPermissions'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    redirect: vi.fn((path: string) => ({ type: 'redirect', path })),
  }
})

vi.mock('@/app/AppRouter/utils/getUserDefaultPath', () => ({
  getUserDefaultPath: vi.fn(() => '/mocked-default-path'),
}))

const setupStore = (options: {
  hasUser?: boolean
  hasVenueSelected?: boolean
  isFeatureActive?: boolean
  hasVenue?: boolean
}) => {
  const store = configureTestStore({
    features: {
      list: options.isFeatureActive
        ? [{ id: 1, isActive: true, name: 'WIP_SWITCH_VENUE' }]
        : [],
    },
    user: {
      access: null,
      currentUser: options.hasUser ? sharedCurrentUserFactory() : null,
      selectedAdminOfferer: null,
      selectedVenue: options.hasVenueSelected
        ? makeGetVenueResponseModel({ id: 1 })
        : null,
      venues: options.hasVenue
        ? [
            makeVenueListItemLiteResponseModel({
              id: 3,
              managingOffererId: 1,
              name: 'Digital Venue A1',
            }),
          ]
        : null,
      venuesWithPendingValidation: null,
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
          hasVenueSelected: true,
          hasVenue: true,
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
          hasVenueSelected: true,
          hasVenue: true,
        })
        const permissionCheck = (_: UserPermissions) => true
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)
        const result = guardedLoader(args)

        expect(result).toBeNull()
      })
    })

    describe('when user is not allowed', () => {
      it('should redirect to the user default path', () => {
        setupStore({ isFeatureActive: true, hasUser: false })
        const permissionCheck = (_: UserPermissions) => false
        const args = createMockLoaderArgs('http://localhost/some-page')

        const guardedLoader = withUserPermissions(permissionCheck)

        expect(() => guardedLoader(args)).toThrow()
        expect(reactRouter.redirect).toHaveBeenCalledWith(
          '/mocked-default-path'
        )
      })
    })
  })
})
