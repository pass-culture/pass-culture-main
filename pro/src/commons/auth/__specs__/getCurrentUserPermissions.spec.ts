import { VenueState } from '@/apiClient/v1'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  makeUserSliceState,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { COOKIES } from '@/commons/utils/localStorageManager'

import { getCurrentUserPermissions } from '../getCurrentUserPermissions'

function mockCookie(value: string) {
  Object.defineProperty(document, 'cookie', { writable: true, value })
}

describe('getCurrentUserPermissions', () => {
  beforeEach(() => {
    mockCookie('')
  })

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
        isSelectedPartnerVenueActive: false,
        isSelectedPartnerVenueAssociated: false,
        isSelectedPartnerVenueOnboarded: false,
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
        isSelectedPartnerVenueAssociated: false,
        isSelectedPartnerVenueOnboarded: false,
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
          isSelectedPartnerVenueAssociated: false,
          isSelectedPartnerVenueOnboarded: false,
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
          isSelectedPartnerVenueAssociated: false,
          isSelectedPartnerVenueOnboarded: false,
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
            isSelectedPartnerVenueActive: false,
            isSelectedPartnerVenueAssociated: false,
            isSelectedPartnerVenueOnboarded: false,
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
            isSelectedPartnerVenueActive: true,
            isSelectedPartnerVenueAssociated: true,
            isSelectedPartnerVenueOnboarded: false,
          })
        })

        describe('when venue is not onboarded', () => {
          it('should return isSelectedPartnerVenueOnboarded as false', () => {
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
              isSelectedPartnerVenueAssociated: true,
              isSelectedPartnerVenueOnboarded: false,
            })
          })
        })

        describe('when venue is closed', () => {
          it.each([
            VenueState.CLOSED,
            VenueState.CLOSING,
          ])('should return isSelectedPartnerVenueActive as false when venue state is %s', (venueState) => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: fakeVenue.id,
                isOnboarded: true,
                state: venueState,
              }),
              venues: fakeVenues,
              venuesWithPendingValidation: null,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedPartnerVenue: true,
              isSelectedPartnerVenueActive: false,
            })
          })
        })

        describe('when venue is not onboarded but onboarding was skipped', () => {
          it('should return isSelectedPartnerVenueOnboarded as true', () => {
            mockCookie(`${COOKIES.DID_SKIP_ONBOARDING}=true`)
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
              isSelectedPartnerVenueOnboarded: true,
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
              isSelectedPartnerVenueAssociated: false,
              isSelectedPartnerVenueOnboarded: false,
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
              isSelectedPartnerVenueActive: true,
              isSelectedPartnerVenueAssociated: true,
              isSelectedPartnerVenueOnboarded: true,
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
            offererNames: null,
            selectedAdminOfferer: null,
            venues: fakeVenues,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedAdminOfferer: false,
            hasVenues: true,
            isAuthenticated: true,
            isSelectedAdminOffererAssociated: false,
            isSelectedPartnerVenueOnboarded: false,
          })
        })
      })

      describe('with selected admin offerer', () => {
        const fakeAdminOfferer = defaultGetOffererResponseModel

        it('should return hasSelectedAdminOfferer as true', () => {
          const userSliceState = makeUserSliceState({
            currentUser: fakeCurrentUser,
            offererNames: [
              {
                id: fakeAdminOfferer.id,
                name: fakeAdminOfferer.name,
                validated: true,
              },
            ],
            selectedAdminOfferer: fakeAdminOfferer,
            venues: fakeVenues,
          })

          const result = getCurrentUserPermissions(userSliceState)

          expect(result).toMatchObject({
            hasSelectedAdminOfferer: true,
            hasVenues: true,
            isAuthenticated: true,
            isSelectedAdminOffererAssociated: true,
            isSelectedPartnerVenueOnboarded: false,
          })
        })

        describe('when selected admin offerer is part of offerer names with pending validation', () => {
          it('should return isSelectedAdminOffererAssociated as false', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              offererNames: [
                {
                  id: fakeAdminOfferer.id,
                  name: fakeAdminOfferer.name,
                  validated: false,
                },
              ],
              selectedAdminOfferer: fakeAdminOfferer,
              venues: fakeVenues,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedAdminOfferer: true,
              hasVenues: true,
              isAuthenticated: true,
              isSelectedAdminOffererAssociated: false,
              isSelectedPartnerVenueOnboarded: false,
            })
          })
        })

        describe('when selected admin offerer is not part of offerer names with pending validation', () => {
          it('should return isSelectedAdminOffererAssociated as true', () => {
            const userSliceState = makeUserSliceState({
              currentUser: fakeCurrentUser,
              offererNames: [
                {
                  id: fakeAdminOfferer.id,
                  name: fakeAdminOfferer.name,
                  validated: true,
                },
              ],
              selectedAdminOfferer: fakeAdminOfferer,
              venues: fakeVenues,
            })

            const result = getCurrentUserPermissions(userSliceState)

            expect(result).toMatchObject({
              hasSelectedAdminOfferer: true,
              hasVenues: true,
              isAuthenticated: true,
              isSelectedAdminOffererAssociated: true,
              isSelectedPartnerVenueOnboarded: false,
            })
          })
        })
      })
    })
  })
})
