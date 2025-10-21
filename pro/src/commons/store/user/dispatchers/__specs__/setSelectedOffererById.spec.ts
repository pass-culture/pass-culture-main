import { vi } from 'vitest'

import { api } from '@/apiClient/api'

vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))

import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'

import { setCurrentOffererById } from '../setSelectedOffererById'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
}))

describe('setCurrentOffererById', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  const mockedApi = api as unknown as {
    getVenues: ReturnType<typeof vi.fn>
    listOfferersNames: ReturnType<typeof vi.fn>
    getOfferer: ReturnType<typeof vi.fn>
    signout: ReturnType<typeof vi.fn>
  }

  it('should early-return when nextCurrentOffererId equals previous currentOfferer id', async () => {
    const preloaded = {
      offerer: {
        offererNames: null,
        currentOfferer: { id: 42, isOnboarded: true, name: 'X' },
      },
      user: {
        currentUser: null,
        access: null,
        selectedVenue: null,
        venues: [],
      },
    } as unknown as Partial<RootState>

    const store = configureTestStore(preloaded)

    await store
      .dispatch(setCurrentOffererById({ nextCurrentOffererId: 42 }))
      .unwrap()

    expect(api.getOfferer).not.toHaveBeenCalled()
    expect(api.getVenues).not.toHaveBeenCalled()
    expect(api.listOfferersNames).not.toHaveBeenCalled()
  })

  it('should refetch offerers/venues, set access, currentOfferer, selectedVenue and persist ids', async () => {
    const venues = [
      { id: 10, name: 'A', managingOffererId: 7 },
      { id: 11, name: 'B', managingOffererId: 7 },
      { id: 12, name: 'C', managingOffererId: 9 },
    ]
    const offerersNames = { offerersNames: [{ id: 7, name: 'Offerer 7' }] }
    mockedApi.getVenues.mockResolvedValue({ venues })
    mockedApi.listOfferersNames.mockResolvedValue(offerersNames)
    mockedApi.getOfferer.mockResolvedValue({
      id: 7,
      isOnboarded: false,
      name: 'Offerer 7',
    })

    const preloaded = {
      offerer: { offererNames: null, currentOfferer: null },
      user: {
        currentUser: null,
        access: null,
        selectedVenue: null,
        venues: [],
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store
      .dispatch(
        setCurrentOffererById({ nextCurrentOffererId: 7, shouldRefetch: true })
      )
      .unwrap()

    const state = store.getState()

    expect(state.offerer.offererNames).toEqual(offerersNames.offerersNames)
    expect(state.user.venues).toEqual(venues)
    expect(state.offerer.currentOfferer?.id).toBe(7)
    expect(state.user.selectedVenue?.managingOffererId).toBe(7)
    // isOnboarded: false -> no-onboarding
    expect(state.user.access).toBe('no-onboarding')
    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('7')
    expect(['10', '11']).toContain(localStorage.getItem(SAVED_VENUE_ID_KEY))
  })

  it('should use existing venues when shouldRefetch=false and set access full', async () => {
    const venues = [
      { id: 21, name: 'A', managingOffererId: 5 },
      { id: 22, name: 'B', managingOffererId: 5 },
    ]
    mockedApi.getOfferer.mockResolvedValue({
      id: 5,
      isOnboarded: true,
      name: 'Offerer 5',
    })

    const preloaded = {
      offerer: {
        offererNames: null,
        currentOfferer: { id: 99, isOnboarded: true, name: 'Old' },
      },
      user: { currentUser: null, access: null, selectedVenue: null, venues },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store
      .dispatch(setCurrentOffererById({ nextCurrentOffererId: 5 }))
      .unwrap()

    const state = store.getState()
    expect(api.getVenues).not.toHaveBeenCalled()
    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(state.offerer.currentOfferer?.id).toBe(5)
    expect(state.user.selectedVenue?.id).toBe(21)
    expect(state.user.access).toBe('full')
  })

  it('should set access to unattached on 403 ApiError and not throw', async () => {
    mockedApi.getOfferer.mockRejectedValue({
      name: 'ApiError',
      message: 'Forbidden',
      status: 403,
      body: {},
    })

    const preloaded = {
      offerer: { offererNames: null, currentOfferer: null },
      user: {
        currentUser: null,
        access: null,
        selectedVenue: null,
        venues: [],
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await store
      .dispatch(setCurrentOffererById({ nextCurrentOffererId: 1 }))
      .unwrap()

    expect(store.getState().user.access).toBe('unattached')
  })

  it('should throw when no venue matches the offerer (assertOrFrontendError path)', async () => {
    mockedApi.getOfferer.mockResolvedValue({
      id: 123,
      isOnboarded: true,
      name: 'O',
    })

    const preloaded = {
      offerer: { offererNames: null, currentOfferer: null },
      user: {
        currentUser: null,
        access: null,
        selectedVenue: null,
        venues: [],
      },
    } as unknown as Partial<RootState>
    const store = configureTestStore(preloaded)

    await expect(
      store
        .dispatch(setCurrentOffererById({ nextCurrentOffererId: 123 }))
        .unwrap()
    ).rejects.toThrow('`nextSelectedVenue` is undefined.')
  })
})
