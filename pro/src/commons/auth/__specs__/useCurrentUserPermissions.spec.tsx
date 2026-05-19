import { act, renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from '@/commons/store/testUtils'
import {
  setSelectedPartnerVenue,
  type UserSliceState,
} from '@/commons/store/user/reducer'
import {
  makeUserSliceState,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'

import { useCurrentUserPermissions } from '../useCurrentUserPermissions'

const renderUseCurrentUserPermissions = (
  initialUserSliceState: UserSliceState
) => {
  const store = configureTestStore({ user: initialUserSliceState })
  const wrapper = ({ children }: { children: ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  )

  return {
    ...renderHook(() => useCurrentUserPermissions(), { wrapper }),
    store,
  }
}

describe('useCurrentUserPermissions', () => {
  const fakeVenueId = 1
  const fakeVenue = makeGetVenueResponseModel({
    id: fakeVenueId,
    isOnboarded: false,
  })
  const fakeVenueLite = makeVenueListItemLiteResponseModel({ id: fakeVenueId })

  it('should refresh permissions when the user slice state changes changes', () => {
    const initialUserSliceState = makeUserSliceState({
      currentUser: sharedCurrentUserFactory(),
      selectedPartnerVenue: fakeVenue,
      venues: [fakeVenueLite],
    })

    const { result, store } = renderUseCurrentUserPermissions(
      initialUserSliceState
    )

    expect(result.current.hasSelectedPartnerVenue).toBe(true)
    expect(result.current.isOnboarded).toBe(false)

    act(() => {
      store.dispatch(
        setSelectedPartnerVenue({ ...fakeVenue, isOnboarded: true })
      )
    })

    expect(result.current.hasSelectedPartnerVenue).toBe(true)
    expect(result.current.isOnboarded).toBe(true)
  })

  it('should return a stable reference between renders when the user slice state is unchanged', () => {
    const initialUserSliceState = makeUserSliceState({
      currentUser: sharedCurrentUserFactory(),
      selectedPartnerVenue: fakeVenue,
      venues: [fakeVenueLite],
    })

    const { result, rerender } = renderUseCurrentUserPermissions(
      initialUserSliceState
    )

    const firstResult = result.current
    rerender()

    expect(result.current).toBe(firstResult)
  })
})
