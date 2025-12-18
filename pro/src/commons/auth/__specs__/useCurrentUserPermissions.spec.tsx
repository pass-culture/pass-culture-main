import { renderHook } from '@testing-library/react'
import type { PropsWithChildren } from 'react'
import { Provider } from 'react-redux'

import type {
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
} from '@/apiClient/v1'
import { configureTestStore } from '@/commons/store/testUtils'
import type { UserAccess } from '@/commons/store/user/reducer'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { useCurrentUserPermissions } from '../useCurrentUserPermissions'

const renderUseCurrentUserPermissions = ({
  currentUser,
  access,
  selectedVenue,
}: {
  currentUser: SharedCurrentUserResponseModel | null
  access: UserAccess | null
  selectedVenue: GetVenueResponseModel | null
}) => {
  const store = configureTestStore({
    user: { currentUser, access, selectedVenue, venues: null },
  })

  const wrapper = ({ children }: PropsWithChildren) => (
    <Provider store={store}>{children}</Provider>
  )

  return renderHook(() => useCurrentUserPermissions(), { wrapper })
}

describe('useCurrentUserPermissions()', () => {
  describe('when user is not logged in', () => {
    it('should return unauthenticated permissions', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: null,
        access: null,
        selectedVenue: null,
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: false,
        isAuthenticated: false,
        isOnboarded: false,
        isSelectedVenueAssociated: false,
      })
    })
  })

  describe('when user is logged in', () => {
    it('should return authenticated without venue when no venue is selected', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: sharedCurrentUserFactory(),
        access: 'full',
        selectedVenue: null,
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: false,
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedVenueAssociated: false,
      })
    })

    it('should return unassociated venue when user has unattached access', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: sharedCurrentUserFactory(),
        access: 'unattached',
        selectedVenue: makeGetVenueResponseModel({ id: 1 }),
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: true,
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedVenueAssociated: false,
      })
    })

    it('should return not onboarded when user has no-onboarding access', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: sharedCurrentUserFactory(),
        access: 'no-onboarding',
        selectedVenue: makeGetVenueResponseModel({ id: 1 }),
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: true,
        isAuthenticated: true,
        isOnboarded: false,
        isSelectedVenueAssociated: true,
      })
    })

    it('should return fully onboarded when user has full access with selected venue', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: sharedCurrentUserFactory(),
        access: 'full',
        selectedVenue: makeGetVenueResponseModel({ id: 1 }),
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: true,
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedVenueAssociated: true,
      })
    })

    it('should return not onboarded when user has no-offerer access', () => {
      const { result } = renderUseCurrentUserPermissions({
        currentUser: sharedCurrentUserFactory(),
        access: 'no-offerer',
        selectedVenue: makeGetVenueResponseModel({ id: 1 }),
      })

      expect(result.current).toStrictEqual({
        hasSelectedVenue: true,
        isAuthenticated: true,
        isOnboarded: true,
        isSelectedVenueAssociated: true,
      })
    })
  })
})
