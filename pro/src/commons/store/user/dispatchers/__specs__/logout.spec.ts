import { vi } from 'vitest'

import { api } from '@/apiClient/api'

vi.mock('@/commons/errors/handleError', () => ({ handleError: vi.fn() }))

import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { configureTestStore } from '@/commons/store/testUtils'

import { logout } from '../logout'

vi.mock('@/apiClient/api', () => ({
  api: {
    signout: vi.fn(),
  },
}))

describe('logout', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  it('should signout, clear localStorage, and reset related slices', async () => {
    const store = configureTestStore({
      offerer: {
        offererNames: [{ id: 1, name: 'O' }],
        currentOfferer: { id: 1, isOnboarded: true, name: 'O' },
      },
      user: {
        currentUser: {
          dateCreated: '2025-01-01T00:00:00Z',
          email: 'a@b.c',
          id: 1,
          isEmailValidated: true,
          roles: [],
        } satisfies SharedCurrentUserResponseModel,
        access: 'full',
        selectedVenue: {
          id: 2,
          name: 'V',
          offererName: 'O',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          managingOffererId: 1,
          venueTypeCode: 'Autre',
        },
        venues: [
          {
            id: 2,
            name: 'V',
            offererName: 'O',
            isVirtual: false,
            isPermanent: true,
            isCaledonian: false,
            hasCreatedOffer: false,
            managingOffererId: 1,
            venueTypeCode: 'Autre',
          },
        ],
      },
    } as unknown as Partial<import('@/commons/store/store').RootState>)

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '1')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '2')

    await store.dispatch(logout()).unwrap()

    const state = store.getState()
    expect(state.offerer.offererNames).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.user.currentUser).toBeNull()
    expect(state.user.access).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()
    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBeNull()
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('should handle signout error gracefully and still reset state', async () => {
    ;(api.signout as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('network')
    )

    const store = configureTestStore()
    await store.dispatch(logout()).unwrap()

    const state = store.getState()
    expect(state.user.currentUser).toBeNull()
  })
})
