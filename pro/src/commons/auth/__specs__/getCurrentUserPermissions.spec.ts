import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
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
          selectedAdminOfferer: null,
          selectedPartnerVenue: null,
          venues: null,
          venuesWithPendingValidation: null,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

      const result = getCurrentUserPermissions()

      expect(result).toEqual({
        hasSelectedAdminOfferer: false,
        hasSelectedPartnerVenue: false,
        isAuthenticated: false,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: false,
      })
    })
  })

  describe('when user is authenticated', () => {
    it('should return isAuthenticated as true', () => {
      const store = configureTestStore({
        user: {
          access: null,
          currentUser: sharedCurrentUserFactory(),
          selectedAdminOfferer: null,
          selectedPartnerVenue: null,
          venues: null,
          venuesWithPendingValidation: null,
        },
      })
      vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

      const result = getCurrentUserPermissions()

      expect(result.isAuthenticated).toBe(true)
    })

    describe('without selected venue', () => {
      it('should return hasSelectedPartnerVenue as false', () => {
        const store = configureTestStore({
          user: {
            access: null,
            currentUser: sharedCurrentUserFactory(),
            selectedAdminOfferer: null,
            selectedPartnerVenue: null,
            venues: null,
            venuesWithPendingValidation: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result.hasSelectedPartnerVenue).toBe(false)
        expect(result.isSelectedPartnerVenueAssociated).toBe(false)
        expect(result.isOnboarded).toBe(false)
      })
    })

    describe('with selected admin offerer', () => {
      it('should return hasSelectedAdminOfferer as true', () => {
        const store = configureTestStore({
          user: {
            access: null,
            currentUser: sharedCurrentUserFactory(),
            selectedAdminOfferer: {
              ...defaultGetOffererResponseModel,
              id: 100,
            },
            selectedPartnerVenue: null,
            venues: null,
            venuesWithPendingValidation: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result.hasSelectedAdminOfferer).toBe(true)
      })
    })

    describe('with selected venue', () => {
      it('should return hasSelectedPartnerVenue as true', () => {
        const store = configureTestStore({
          user: {
            access: null,
            currentUser: sharedCurrentUserFactory(),
            selectedAdminOfferer: null,
            selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
            venues: null,
            venuesWithPendingValidation: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result.hasSelectedPartnerVenue).toBe(true)
      })

      describe('when access is unattached', () => {
        it('should return isSelectedPartnerVenueAssociated as false', () => {
          const store = configureTestStore({
            user: {
              access: 'unattached' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result.isSelectedPartnerVenueAssociated).toBe(false)
          expect(result.isOnboarded).toBe(false)
        })
      })

      describe('when access is no-onboarding', () => {
        it('should return isSelectedPartnerVenueAssociated as true but isOnboarded as false', () => {
          const store = configureTestStore({
            user: {
              access: 'no-onboarding' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result.isSelectedPartnerVenueAssociated).toBe(true)
          expect(result.isOnboarded).toBe(false)
        })
      })

      describe('when access is full', () => {
        it('should return all permissions as true', () => {
          const store = configureTestStore({
            user: {
              access: 'full' as UserAccess,
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
              venues: null,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedAdminOfferer: false,
            hasSelectedPartnerVenue: true,
            isAuthenticated: true,
            isOnboarded: true,
            isSelectedPartnerVenueAssociated: true,
          })
        })
      })
    })
  })
})
