import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { getCurrentUserPermissions } from '../getCurrentUserPermissions'

describe('getCurrentUserPermissions', () => {
  describe('when user is not authenticated', () => {
    it('should return all permissions as false', () => {
      const store = configureTestStore({
        user: {
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
          currentUser: sharedCurrentUserFactory(),
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
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: false,
      })
    })

    describe('without selected venue', () => {
      it('should return hasSelectedPartnerVenue as false', () => {
        const store = configureTestStore({
          user: {
            currentUser: sharedCurrentUserFactory(),
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
          isAuthenticated: true,
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: false,
        })
      })
    })

    describe('with selected admin offerer', () => {
      it('should return hasSelectedAdminOfferer as true', () => {
        const store = configureTestStore({
          user: {
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

        expect(result).toEqual({
          hasSelectedAdminOfferer: true,
          hasSelectedPartnerVenue: false,
          isAuthenticated: true,
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: false,
        })
      })
    })

    describe('with selected venue', () => {
      it('should return hasSelectedPartnerVenue as true', () => {
        const store = configureTestStore({
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedAdminOfferer: null,
            selectedPartnerVenue: makeGetVenueResponseModel({
              id: 1,
              isOnboarded: false,
            }),
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
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: true,
        })
      })

      describe('when venue is not onboarded', () => {
        it('should return isOnboarded as false', () => {
          const store = configureTestStore({
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: 1,
                isOnboarded: false,
              }),
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
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: true,
          })
        })
      })

      describe('when selected venue is part of venues with pending validation', () => {
        it('should return isSelectedPartnerVenueAssociated as false', () => {
          const selectedPartnerVenueId = 1

          const store = configureTestStore({
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: selectedPartnerVenueId,
                isOnboarded: false,
              }),
              venues: null,
              venuesWithPendingValidation: [{ id: selectedPartnerVenueId }],
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedAdminOfferer: false,
            hasSelectedPartnerVenue: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: false,
          })
        })
      })

      describe('when access is full', () => {
        it('should return all permissions as true', () => {
          const store = configureTestStore({
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: 1,
                isOnboarded: true,
              }),
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
