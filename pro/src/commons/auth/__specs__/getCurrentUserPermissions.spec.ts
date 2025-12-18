import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { getCurrentUserPermissions } from '../getCurrentUserPermissions'

describe('getCurrentUserPermissions', () => {
  describe('when user is not authenticated', () => {
    it('should return all permissions as false', () => {
      const store = configureTestStore({
        user: {
          access: null,
          currentUser: null,
          selectedVenue: null,
          venues: null,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

      const result = getCurrentUserPermissions()

      expect(result).toEqual({
        hasSelectedVenue: false,
        isAuthenticated: false,
        isOnboarded: false,
        isSelectedVenueAssociated: false,
      })
    })
  })

  describe('when user is authenticated', () => {
    it('should return isAuthenticated as true', () => {
      const store = configureTestStore({
        user: {
          access: null,
          currentUser: sharedCurrentUserFactory(),
          selectedVenue: null,
          venues: null,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

      const result = getCurrentUserPermissions()

      expect(result.isAuthenticated).toBe(true)
    })

    describe('without selected venue', () => {
      it('should return hasSelectedVenue as false', () => {
        const store = configureTestStore({
          user: {
            access: null,
            currentUser: sharedCurrentUserFactory(),
            selectedVenue: null,
            venues: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result.hasSelectedVenue).toBe(false)
        expect(result.isSelectedVenueAssociated).toBe(false)
        expect(result.isOnboarded).toBe(false)
      })
    })

    describe('with selected venue', () => {
      it('should return hasSelectedVenue as true', () => {
        const store = configureTestStore({
          user: {
            access: null,
            currentUser: sharedCurrentUserFactory(),
            selectedVenue: makeGetVenueResponseModel({ id: 1 }),
            venues: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result.hasSelectedVenue).toBe(true)
      })

      describe('when access is unattached', () => {
        it('should return isSelectedVenueAssociated as false', () => {
          const store = configureTestStore({
            user: {
              access: 'unattached' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result.isSelectedVenueAssociated).toBe(false)
          expect(result.isOnboarded).toBe(false)
        })
      })

      describe('when access is no-onboarding', () => {
        it('should return isSelectedVenueAssociated as true but isOnboarded as false', () => {
          const store = configureTestStore({
            user: {
              access: 'no-onboarding' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result.isSelectedVenueAssociated).toBe(true)
          expect(result.isOnboarded).toBe(false)
        })
      })

      describe('when access is full', () => {
        it('should return all permissions as true', () => {
          const store = configureTestStore({
            user: {
              access: 'full' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedVenue: true,
            isAuthenticated: true,
            isOnboarded: true,
            isSelectedVenueAssociated: true,
          })
        })
      })
    })
  })
})
