import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'

import { setSelectedVenueById } from '../setSelectedVenueById'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
  },
}))

describe('setSelectedVenueById', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  const mockedApi = api as unknown as {
    getOfferer: ReturnType<typeof vi.fn>
  }

  it('should early-return when selecting the same venue', async () => {
    const preloaded = {
      user: {
        currentUser: null,
        access: null,
        venues: [
          { id: 1, name: 'V1', managingOffererId: 5 },
          { id: 2, name: 'V2', managingOffererId: 6 },
        ],
        selectedVenue: { id: 2, name: 'V2', managingOffererId: 6 },
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store.dispatch(setSelectedVenueById(2)).unwrap()

    expect(mockedApi.getOfferer).not.toHaveBeenCalled()
  })

  it('should compute nextSelectedVenue, fetch offerer, update access and persist', async () => {
    mockedApi.getOfferer.mockResolvedValue({
      id: 6,
      isOnboarded: true,
      name: 'O',
    })

    const preloaded = {
      user: {
        currentUser: null,
        access: null,
        venues: [
          { id: 1, name: 'V1', managingOffererId: 5 },
          { id: 2, name: 'V2', managingOffererId: 6 },
        ],
        selectedVenue: { id: 1, name: 'V1', managingOffererId: 5 },
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store.dispatch(setSelectedVenueById(2)).unwrap()

    const state = store.getState()
    expect(state.user.selectedVenue?.id).toBe(2)
    expect(state.offerer.currentOfferer?.id).toBe(6)
    expect(state.user.access).toBe('full')
    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('6')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('2')
  })

  it('should fallback to first venue when requested one is unknown', async () => {
    mockedApi.getOfferer.mockResolvedValue({
      id: 5,
      isOnboarded: false,
      name: 'O',
    })

    const preloaded = {
      user: {
        currentUser: null,
        access: null,
        venues: [
          { id: 10, name: 'A', managingOffererId: 5 },
          { id: 11, name: 'B', managingOffererId: 6 },
        ],
        selectedVenue: { id: 11, name: 'B', managingOffererId: 6 },
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store.dispatch(setSelectedVenueById(999)).unwrap()

    expect(store.getState().user.selectedVenue?.id).toBe(10)
    expect(store.getState().user.access).toBe('no-onboarding')
  })

  it('should set access to unattached on 403 ApiError', async () => {
    mockedApi.getOfferer.mockRejectedValue({
      name: 'ApiError',
      message: 'Forbidden',
      status: 403,
      body: {},
    })

    const preloaded = {
      user: {
        currentUser: null,
        access: null,
        venues: [{ id: 1, name: 'V1', managingOffererId: 5 }],
        selectedVenue: { id: 1, name: 'V1', managingOffererId: 5 },
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store.dispatch(setSelectedVenueById(2)).unwrap()

    expect(store.getState().user.access).toBe('unattached')
  })
})
