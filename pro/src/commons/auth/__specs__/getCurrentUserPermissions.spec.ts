import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

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
        hasVenues: false,
        isAuthenticated: false,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: false,
      })
    })
  })

  describe('when user is authenticated', () => {
    const fakeCurrentUser = sharedCurrentUserFactory()

    it('should return isAuthenticated as true', () => {
      const store = configureTestStore({
        user: {
          currentUser: fakeCurrentUser,
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
        hasVenues: false,
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: false,
      })
    })

    describe('without venues', () => {
      it('should return hasVenues as false', () => {
        const store = configureTestStore({
          user: {
            currentUser: fakeCurrentUser,
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
          hasVenues: false,
          isAuthenticated: true,
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: false,
        })
      })
    })

    describe('with venues', () => {
      const fakeVenue = makeVenueListItemLiteResponseModel({ id: 1 })
      const fakeVenues = [fakeVenue]

      it('should return hasVenues as true', () => {
        const store = configureTestStore({
          user: {
            currentUser: fakeCurrentUser,
            selectedAdminOfferer: null,
            selectedPartnerVenue: null,
            venues: fakeVenues,
            venuesWithPendingValidation: null,
          },
        })
        vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

        const result = getCurrentUserPermissions()

        expect(result).toEqual({
          hasSelectedAdminOfferer: false,
          hasSelectedPartnerVenue: false,
          hasVenues: true,
          isAuthenticated: true,
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: false,
        })
      })

      describe('without selected partner venue', () => {
        it('should return hasSelectedPartnerVenue as false', () => {
          const store = configureTestStore({
            user: {
              currentUser: fakeCurrentUser,
              selectedAdminOfferer: null,
              selectedPartnerVenue: null,
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedAdminOfferer: false,
            hasSelectedPartnerVenue: false,
            hasVenues: true,
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
              currentUser: fakeCurrentUser,
              selectedAdminOfferer: null,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: fakeVenue.id,
                isOnboarded: false,
              }),
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedAdminOfferer: false,
            hasSelectedPartnerVenue: true,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: true,
          })
        })

        describe('when venue is not onboarded', () => {
          it('should return isOnboarded as false', () => {
            const store = configureTestStore({
              user: {
                currentUser: fakeCurrentUser,
                selectedAdminOfferer: null,
                selectedPartnerVenue: makeGetVenueResponseModel({
                  id: fakeVenue.id,
                  isOnboarded: false,
                }),
                venues: fakeVenues,
                venuesWithPendingValidation: null,
              },
            })
            vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

            const result = getCurrentUserPermissions()

            expect(result).toEqual({
              hasSelectedAdminOfferer: false,
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedPartnerVenueAssociated: true,
            })
          })
        })

        describe('when selected venue is part of venues with pending validation', () => {
          it('should return isSelectedPartnerVenueAssociated as false', () => {
            const store = configureTestStore({
              user: {
                currentUser: fakeCurrentUser,
                selectedAdminOfferer: null,
                selectedPartnerVenue: makeGetVenueResponseModel({
                  id: fakeVenue.id,
                  isOnboarded: false,
                }),
                venues: fakeVenues,
                venuesWithPendingValidation: fakeVenues,
              },
            })
            vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

            const result = getCurrentUserPermissions()

            expect(result).toEqual({
              hasSelectedAdminOfferer: false,
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedPartnerVenueAssociated: false,
            })
          })
        })

        describe('when selected venue is both onboarded and not part of venues with pending validation', () => {
          it('should return all venue-related permissions as true', () => {
            const store = configureTestStore({
              user: {
                currentUser: fakeCurrentUser,
                selectedAdminOfferer: null,
                selectedPartnerVenue: makeGetVenueResponseModel({
                  id: fakeVenue.id,
                  isOnboarded: true,
                }),
                venues: fakeVenues,
                venuesWithPendingValidation: null,
              },
            })
            vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

            const result = getCurrentUserPermissions()

            expect(result).toEqual({
              hasSelectedAdminOfferer: false,
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: true,
              isSelectedPartnerVenueAssociated: true,
            })
          })
        })
      })

      describe('with selected admin offerer', () => {
        const fakeAdminOfferer = defaultGetOffererResponseModel

        it('should return hasSelectedAdminOfferer as true', () => {
          const store = configureTestStore({
            user: {
              currentUser: fakeCurrentUser,
              selectedAdminOfferer: fakeAdminOfferer,
              selectedPartnerVenue: null,
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            },
          })
          vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)

          const result = getCurrentUserPermissions()

          expect(result).toEqual({
            hasSelectedAdminOfferer: true,
            hasSelectedPartnerVenue: false,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: false,
          })
        })
      })
    })
  })
})
