import type { FeatureResponseModel } from '@/apiClient/v1'
import type { UserPermissions } from '@/commons/auth/types'
import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { COOKIES } from '@/commons/utils/localStorageManager'

import {
  isNewHomepageEnabled,
  isSwitchVenueEnabled,
  mustBeAuthenticated,
  mustBeOnboardedOrSkipped,
  mustBeOnboardedWithSelectedPartnerVenue,
  mustBeUnauthenticated,
  mustHaveSelectedAdminOfferer,
  mustNotBeOnboardedWithSelectedPartnerVenue,
} from '../utils'

const makeUserPermissions = (
  overrides: Partial<UserPermissions> = {}
): UserPermissions => ({
  isAuthenticated: false,
  hasSelectedPartnerVenue: false,
  isOnboarded: false,
  isSelectedPartnerVenueAssociated: false,
  hasSelectedAdminOfferer: false,
  ...overrides,
})

function mockCookie(value: string) {
  Object.defineProperty(document, 'cookie', { writable: true, value })
}
describe('utils', () => {
  describe('mustBeAuthenticated', () => {
    it('should return true when user is authenticated', () => {
      const permissions = makeUserPermissions({ isAuthenticated: true })

      expect(mustBeAuthenticated(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({ isAuthenticated: false })

      expect(mustBeAuthenticated(permissions)).toBe(false)
    })
  })

  describe('mustBeUnauthenticated', () => {
    it('should return true when user is not authenticated', () => {
      const permissions = makeUserPermissions({ isAuthenticated: false })

      expect(mustBeUnauthenticated(permissions)).toBe(true)
    })

    it('should return false when user is authenticated', () => {
      const permissions = makeUserPermissions({ isAuthenticated: true })

      expect(mustBeUnauthenticated(permissions)).toBe(false)
    })
  })

  describe('mustBeOnboardedOrSkipped', () => {
    it('should return true when user is onboarded whatever the sessions storage value is', () => {
      mockCookie('')
      const permissions = makeUserPermissions({
        isOnboarded: true,
      })
      expect(mustBeOnboardedOrSkipped(permissions)).toBe(true)

      mockCookie(`${COOKIES.DID_SKIP_ONBOARDING}=true`)
      expect(mustBeOnboardedOrSkipped(permissions)).toBe(true)
    })

    it('should return false when user is not onboarded with no cookie', () => {
      mockCookie('')
      const permissions = makeUserPermissions({
        isOnboarded: false,
      })

      expect(mustBeOnboardedOrSkipped(permissions)).toBe(false)
    })

    it('should return true when user is not onboarded with the cookie set', () => {
      mockCookie(`${COOKIES.DID_SKIP_ONBOARDING}=true`)
      const permissions = makeUserPermissions({
        isOnboarded: false,
      })

      expect(mustBeOnboardedOrSkipped(permissions)).toBe(true)
    })
  })

  describe('mustBeOnboardedWithSelectedPartnerVenue', () => {
    it('should return true when user is authenticated, onboarded, and has associated venue', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: true,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })

    it('should return false when user is not onboarded', () => {
      mockCookie('')
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })

    it('should return false when venue is not associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedPartnerVenueAssociated: false,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })
  })

  describe('mustNotBeOnboardedWithSelectedPartnerVenue', () => {
    it('should return true when user is authenticated but not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: false,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: false,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })

    it('should return false when user is onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })
  })

  describe('mustHaveSelectedAdminOfferer', () => {
    it('should return true when user is authenticated and has selected admin offerer', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        hasSelectedAdminOfferer: true,
      })

      expect(mustHaveSelectedAdminOfferer(permissions)).toBe(true)
    })

    it('should return false when user does not have selected admin offerer', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        hasSelectedAdminOfferer: false,
      })

      expect(mustHaveSelectedAdminOfferer(permissions)).toBe(false)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        hasSelectedAdminOfferer: true,
      })

      expect(mustHaveSelectedAdminOfferer(permissions)).toBe(false)
    })
  })

  describe('hasNewHomepage', () => {
    it.each([
      [false, undefined],
      [false, ['WIP_SWITCH_VENUE']],
      [false, ['WIP_ENABLE_NEW_PRO_HOME']],
      [true, ['WIP_ENABLE_NEW_PRO_HOME', 'WIP_SWITCH_VENUE']],
    ])('should return %s with features=%j', (expectedRes, features) => {
      const store = configureTestStore({
        features: {
          list: (features ?? []).map(
            (feature, index): FeatureResponseModel => ({
              id: index,
              isActive: true,
              name: feature,
            })
          ),
          lastLoaded: 0,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)
      expect(isNewHomepageEnabled()).toBe(expectedRes)
    })
  })

  describe('isSwitchVenueEnabled', () => {
    it.each([
      [false, undefined],
      [true, ['WIP_SWITCH_VENUE']],
    ])('should return %s with features=%j', (expectedRes, features) => {
      const store = configureTestStore({
        features: {
          list: (features ?? []).map(
            (feature, index): FeatureResponseModel => ({
              id: index,
              isActive: true,
              name: feature,
            })
          ),
          lastLoaded: 0,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)
      expect(isSwitchVenueEnabled()).toBe(expectedRes)
    })
  })
})
