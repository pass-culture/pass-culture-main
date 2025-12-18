import type { UserPermissions } from '@/commons/auth/types'

import {
  mustBeAuthenticated,
  mustBeUnauthenticated,
  mustHaveSelectedVenue,
  mustNotBeOnboarded,
} from '../utils'

const makeUserPermissions = (
  overrides: Partial<UserPermissions> = {}
): UserPermissions => ({
  isAuthenticated: false,
  hasSelectedVenue: false,
  isOnboarded: false,
  isSelectedVenueAssociated: false,
  ...overrides,
})

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

  describe('mustHaveSelectedVenue', () => {
    it('should return true when user is authenticated, onboarded, and has associated venue', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedVenueAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: true,
        isSelectedVenueAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(false)
    })

    it('should return false when user is not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedVenueAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(false)
    })

    it('should return false when venue is not associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedVenueAssociated: false,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(false)
    })
  })

  describe('mustNotBeOnboarded', () => {
    it('should return true when user is authenticated but not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: false,
      })

      expect(mustNotBeOnboarded(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: false,
      })

      expect(mustNotBeOnboarded(permissions)).toBe(false)
    })

    it('should return false when user is onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
      })

      expect(mustNotBeOnboarded(permissions)).toBe(false)
    })
  })
})
