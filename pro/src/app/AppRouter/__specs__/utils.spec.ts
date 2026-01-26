import type { UserPermissions } from '@/commons/auth/types'

import {
  mustBeAuthenticated,
  mustBeUnauthenticated,
  mustHaveSelectedVenue,
  mustOnboard,
} from '../utils'

const makeUserPermissions = (
  overrides: Partial<UserPermissions> = {}
): UserPermissions => ({
  hasSelectedVenue: false,
  hasSomeOfferer: false,
  isAuthenticated: false,
  isOnboarded: false,
  isSelectedOffererAssociated: false,
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
        isSelectedOffererAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: true,
        isSelectedOffererAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(false)
    })

    it('should return false when user is not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedOffererAssociated: true,
      })

      expect(mustHaveSelectedVenue(permissions)).toBe(false)
    })

    it('should return false when venue is not associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedOffererAssociated: false,
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

      expect(mustOnboard(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isOnboarded: false,
      })

      expect(mustOnboard(permissions)).toBe(false)
    })

    it('should return false when user is onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isOnboarded: true,
      })

      expect(mustOnboard(permissions)).toBe(false)
    })
  })
})
