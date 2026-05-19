import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  makeUserSliceState,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

import { getCurrentUserPermissions } from '../getCurrentUserPermissions'

describe('getCurrentUserPermissions', () => {
  describe('when user is not authenticated', () => {
    it('should return all permissions as false', () => {
      const userSliceState = makeUserSliceState({
        currentUser: null,
        selectedPartnerVenue: null,
        venues: null,
        venuesWithPendingValidation: null,
      })

      const result = getCurrentUserPermissions(userSliceState)

      expect(result).toMatchObject({
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
      const userSliceState = makeUserSliceState({
        currentUser: fakeCurrentUser,
        selectedPartnerVenue: null,
        venues: null,
        venuesWithPendingValidation: null,
      })

      const result = getCurrentUserPermissions(userSliceState)

      expect(result).toMatchObject({
        hasSelectedPartnerVenue: false,
        hasVenues: false,
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedPartnerVenueAssociated: false,
      })
    })

    describe('without venues', () => {
      it('should return hasVenues as false', () => {
        const userSliceState = makeUserSliceState({
          currentUser: fakeCurrentUser,
          selectedPartnerVenue: null,
          venues: null,
          venuesWithPendingValidation: null,
        })

        const result = getCurrentUserPermissions(userSliceState)

        expect(result).toMatchObject({
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
        const userSliceState = makeUserSliceState({
          currentUser: fakeCurrentUser,
          selectedPartnerVenue: null,
          venues: fakeVenues,
          venuesWithPendingValidation: null,
        })

        const result = getCurrentUserPermissions(userSliceState)

        expect(result).toMatchObject({
          hasSelectedPartnerVenue: false,
          hasVenues: true,
          isAuthenticated: true,
          isOnboarded: false,
          isSelectedPartnerVenueAssociated: false,
        })
      })

      // =======================================================================
      // Partner Space Permissions

      describe('without selected partner venue', () => {
        it('should return hasSelectedPartnerVenue as false', () => {
          const userSliceState = makeUserSliceState({
            currentUser: fakeCurrentUser,
            selectedPartnerVenue: null,
            venues: fakeVenues,
            venuesWithPendingValidation: null,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedPartnerVenue: false,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: false,
          })
        })
      })

      describe('with selected partner venue', () => {
        it('should return hasSelectedPartnerVenue as true', () => {
          const userSliceState = makeUserSliceState({
            currentUser: fakeCurrentUser,
            selectedPartnerVenue: makeGetVenueResponseModel({
              id: fakeVenue.id,
              isOnboarded: false,
            }),
            venues: fakeVenues,
            venuesWithPendingValidation: null,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedPartnerVenue: true,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedPartnerVenueAssociated: true,
          })
        })

        describe('when venue is not onboarded', () => {
          it('should return isOnboarded as false', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: fakeVenue.id,
                isOnboarded: false,
              }),
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedPartnerVenueAssociated: true,
            })
          })
        })

        describe('when selected partner venue is part of venues with pending validation', () => {
          it('should return isSelectedPartnerVenueAssociated as false', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: fakeVenue.id,
                isOnboarded: false,
              }),
              venues: fakeVenues,
              venuesWithPendingValidation: fakeVenues,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedPartnerVenueAssociated: false,
            })
          })
        })

        describe('when selected partner venue is both onboarded and not part of venues with pending validation', () => {
          it('should return all venue-related permissions as true', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: fakeVenue.id,
                isOnboarded: true,
              }),
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedPartnerVenue: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: true,
              isSelectedPartnerVenueAssociated: true,
            })
          })
        })
      })

      // =======================================================================
      // Administration Space Permissions

      describe('without selected admin offerer', () => {
        it('should return hasSelectedAdminOfferer as false', () => {
          const userSliceState = makeUserSliceState({
            currentUser: fakeCurrentUser,
            offerersNamesWithPendingValidation: null,
            selectedAdminOfferer: null,
            venues: fakeVenues,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedAdminOfferer: false,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedAdminOffererAssociated: false,
          })
        })
      })

      describe('with selected admin offerer', () => {
        const fakeAdminOfferer = defaultGetOffererResponseModel

        it('should return hasSelectedAdminOfferer as true', () => {
          const userSliceState = makeUserSliceState({
            currentUser: fakeCurrentUser,
            offerersNamesWithPendingValidation: null,
            selectedAdminOfferer: fakeAdminOfferer,
            venues: fakeVenues,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedAdminOfferer: true,
            hasVenues: true,
            isAuthenticated: true,
            isOnboarded: false,
            isSelectedAdminOffererAssociated: true,
          })
        })

        describe('when selected admin offerer is part of offerer names with pending validation', () => {
          it('should return isSelectedAdminOffererAssociated as false', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              offerersNamesWithPendingValidation: [fakeAdminOfferer],
              selectedAdminOfferer: fakeAdminOfferer,
              venues: fakeVenues,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedAdminOfferer: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedAdminOffererAssociated: false,
            })
          })
        })

        describe('when selected admin offerer is not part of offerer names with pending validation', () => {
          it('should return isSelectedAdminOffererAssociated as true', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              offerersNamesWithPendingValidation: null,
              selectedAdminOfferer: fakeAdminOfferer,
              venues: fakeVenues,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedAdminOfferer: true,
              hasVenues: true,
              isAuthenticated: true,
              isOnboarded: false,
              isSelectedAdminOffererAssociated: true,
            })
          })
        })
      })
    })
  })
})
