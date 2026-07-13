import { makeUserPermissions } from '@/commons/utils/factories/authFactories'

import {
  mustBeAuthenticated,
  mustBeOnboardedWithActiveSelectedPartnerVenue,
  mustBeOnboardedWithSelectedPartnerVenue,
  mustBeUnauthenticated,
  mustHaveSelectedAdminOfferer,
  mustHaveSelectedPartnerVenue,
  mustNotBeOnboardedWithSelectedPartnerVenue,
} from '../utils'

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

  describe('mustHaveSelectedPartnerVenue', () => {
    it('should return true when user is authenticated and venue is associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustHaveSelectedPartnerVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustHaveSelectedPartnerVenue(permissions)).toBe(false)
    })

    it('should return false when venue is not associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueAssociated: false,
      })

      expect(mustHaveSelectedPartnerVenue(permissions)).toBe(false)
    })
  })

  describe('mustBeOnboardedWithSelectedPartnerVenue', () => {
    it('should return true when user is authenticated, onboarded, and has associated venue', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueOnboarded: true,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isSelectedPartnerVenueOnboarded: true,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })

    it('should return false when user is not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueOnboarded: false,
        isSelectedPartnerVenueAssociated: true,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })

    it('should return false when venue is not associated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueOnboarded: true,
        isSelectedPartnerVenueAssociated: false,
      })

      expect(mustBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(false)
    })
  })

  describe('mustBeOnboardedWithActiveSelectedPartnerVenue', () => {
    it('should return true when user is onboarded with an associated and active venue', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: true,
        isSelectedPartnerVenueAssociated: true,
        isSelectedPartnerVenueOnboarded: true,
      })

      expect(mustBeOnboardedWithActiveSelectedPartnerVenue(permissions)).toBe(
        true
      )
    })

    it('should return false when venue is not active', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: false,
        isSelectedPartnerVenueAssociated: true,
        isSelectedPartnerVenueOnboarded: true,
      })

      expect(mustBeOnboardedWithActiveSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })

    it('should return false when user is not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: true,
        isSelectedPartnerVenueAssociated: true,
        isSelectedPartnerVenueOnboarded: false,
      })

      expect(mustBeOnboardedWithActiveSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })
  })

  describe('mustNotBeOnboardedWithSelectedPartnerVenue', () => {
    it('should return true when user is authenticated with an active venue but not onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: true,
        isSelectedPartnerVenueOnboarded: false,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(true)
    })

    it('should return false when user is not authenticated', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: false,
        isSelectedPartnerVenueActive: true,
        isSelectedPartnerVenueOnboarded: false,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })

    it('should return false when user is onboarded', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: true,
        isSelectedPartnerVenueOnboarded: true,
      })

      expect(mustNotBeOnboardedWithSelectedPartnerVenue(permissions)).toBe(
        false
      )
    })

    it('should return false when venue is not active', () => {
      const permissions = makeUserPermissions({
        isAuthenticated: true,
        isSelectedPartnerVenueActive: false,
        isSelectedPartnerVenueOnboarded: false,
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
})
