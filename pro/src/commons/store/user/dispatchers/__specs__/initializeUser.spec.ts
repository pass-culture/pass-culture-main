import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getVenues: vi.fn(),
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
}))

vi.mock('@/commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn(() => true),
}))

import { storageAvailable } from '@/commons/utils/storageAvailable'

import { initializeUser } from '../initializeUser'

const user: SharedCurrentUserResponseModel = {
  dateCreated: '2025-01-01T00:00:00Z',
  email: 'user@pro.fr',
  id: 1,
  isEmailValidated: true,
  roles: [],
}

describe('initializeUser', () => {
  const SAVED_OFFERER_ID_KEY = 'homepageSelectedOffererId'
  const SAVED_VENUE_ID_KEY = 'PASS_CULTURE_SELECTED_VENUE_ID'

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  it('uses saved IDs when storage available and sets full access if onboarded', async () => {
    ;(storageAvailable as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      true
    )
    localStorage.setItem(SAVED_OFFERER_ID_KEY, '99')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '199')

    ;(
      api.listOfferersNames as unknown as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      offerersNames: [{ id: 1, name: 'O1' }],
    })
    ;(api.getVenues as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      venues: [
        {
          id: 199,
          name: 'Saved V',
          managingOffererId: 99,
          offererName: 'O99',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          venueTypeCode: 'Autre',
        },
        {
          id: 11,
          name: 'V11',
          managingOffererId: 1,
          offererName: 'O1',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          venueTypeCode: 'Autre',
        },
      ],
    })
    ;(api.getOfferer as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 99,
      name: 'O99',
      isOnboarded: true,
    })

    const store = configureTestStore() // default initial slices

    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.offerer.offererNames?.[0]?.id).toBe(1)
    expect(state.user.venues?.some((v) => v.id === 199)).toBe(true)
    expect(state.offerer.currentOfferer?.id).toBe(99)
    expect(state.user.selectedVenue?.id).toBe(199)
    expect(state.user.access).toBe('full')
    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('99')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('199')
    expect(state.user.currentUser?.email).toBe('user@pro.fr')
  })

  it('falls back to first IDs when storage unavailable and sets no-onboarding when not onboarded', async () => {
    ;(storageAvailable as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      false
    )

    ;(
      api.listOfferersNames as unknown as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      offerersNames: [{ id: 2, name: 'O2' }],
    })
    ;(api.getVenues as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      venues: [
        {
          id: 20,
          name: 'V20',
          managingOffererId: 2,
          offererName: 'O2',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          venueTypeCode: 'Autre',
        },
      ],
    })
    ;(api.getOfferer as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 2,
      name: 'O2',
      isOnboarded: false,
    })

    const store = configureTestStore()
    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.offerer.currentOfferer?.id).toBe(2)
    expect(state.user.selectedVenue?.id).toBe(20)
    expect(state.user.access).toBe('no-onboarding')
  })

  it('sets no-offerer access when there is no offerer/venue', async () => {
    ;(storageAvailable as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      true
    )
    ;(
      api.listOfferersNames as unknown as ReturnType<typeof vi.fn>
    ).mockResolvedValue({ offerersNames: [] })
    ;(api.getVenues as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      venues: [],
    })

    const store = configureTestStore()
    await store.dispatch(initializeUser(user)).unwrap()

    expect(store.getState().user.access).toBe('no-offerer')
    expect(
      api.getOfferer as unknown as ReturnType<typeof vi.fn>
    ).not.toHaveBeenCalled()
  })

  it('sets unattached when getOfferer rejects with ApiError 403', async () => {
    ;(storageAvailable as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      true
    )
    ;(
      api.listOfferersNames as unknown as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      offerersNames: [{ id: 3, name: 'O3' }],
    })
    ;(api.getVenues as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      venues: [
        {
          id: 30,
          name: 'V30',
          managingOffererId: 3,
          offererName: 'O3',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          venueTypeCode: 'Autre',
        },
      ],
    })
    ;(api.getOfferer as unknown as ReturnType<typeof vi.fn>).mockRejectedValue({
      name: 'ApiError',
      message: 'Forbidden',
      status: 403,
      body: {},
    })

    const store = configureTestStore()
    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.user.access).toBe('unattached')
    expect(state.user.currentUser?.email).toBe('user@pro.fr')
    // localStorage not updated in 403 path
    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBeNull()
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('logs out on non-403 error while initializing selection', async () => {
    ;(storageAvailable as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      true
    )
    ;(
      api.listOfferersNames as unknown as ReturnType<typeof vi.fn>
    ).mockResolvedValue({
      offerersNames: [{ id: 4, name: 'O4' }],
    })
    ;(api.getVenues as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      venues: [
        {
          id: 40,
          name: 'V40',
          managingOffererId: 4,
          offererName: 'O4',
          isVirtual: false,
          isPermanent: true,
          isCaledonian: false,
          hasCreatedOffer: false,
          venueTypeCode: 'Autre',
        },
      ],
    })
    ;(api.getOfferer as unknown as ReturnType<typeof vi.fn>).mockRejectedValue({
      name: 'ApiError',
      message: 'Server error',
      status: 500,
      body: {},
    })

    const store = configureTestStore()
    await store.dispatch(initializeUser(user)).unwrap()

    // After logout, slices should be reset
    const state = store.getState() as RootState
    expect(state.offerer.offererNames).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.user.currentUser).toBeNull()
    expect(state.user.access).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()
  })
})
