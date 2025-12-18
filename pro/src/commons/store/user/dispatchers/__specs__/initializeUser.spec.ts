import { vi } from 'vitest'

import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import { initializeUser } from '../initializeUser'
import * as logoutModule from '../logout'

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getVenue: vi.fn(),
    getVenues: vi.fn(),
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
}))

describe('initializeUser', () => {
  const user = sharedCurrentUserFactory({ email: 'user@pro.fr', id: 1 })

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
    sessionStorage.clear()
    // Reset URL between tests
    window.history.pushState({}, '', '/')
  })

  it('should prioritize BO URL params and refetch names and venues when `structure` search param is present', async () => {
    window.history.pushState({}, '', '/?structure=200')

    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [getOffererNameFactory({ id: 200 })],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [makeVenueListItem({ id: 201, managingOffererId: 200 })],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 200,
      isOnboarded: true,
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 201, managingOffererId: 200 })
    )

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '100')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '101')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.user.access).toBe('full')
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)).toBe(
      '200'
    )
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '201'
    )
  })

  it('should use saved venue id when present and set full access', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({ id: 101, managingOffererId: 100 }),
        makeVenueListItem({ id: 201, managingOffererId: 200 }),
        makeVenueListItem({ id: 202, managingOffererId: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 201, managingOffererId: 200 })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 200,
      isOnboarded: true,
    })

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '200')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '201')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.user.access).toBe('full')
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)).toBe(
      '200'
    )
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '201'
    )
  })

  it('should use saved offerer id when no saved venue id and pick a venue of that offerer', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({ id: 101, managingOffererId: 100 }),
        makeVenueListItem({ id: 201, managingOffererId: 200 }),
        makeVenueListItem({ id: 202, managingOffererId: 200 }),
      ],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 200,
      isOnboarded: true,
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 201, managingOffererId: 200 })
    )

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '200')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.user.access).toBe('full')
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)).toBe(
      '200'
    )
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '201'
    )
  })

  it('should prefer first venue when no saved IDs and mark access according to onboarding=false', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({ id: 101, managingOffererId: 100 }),
        makeVenueListItem({ id: 201, managingOffererId: 200 }),
        makeVenueListItem({ id: 202, managingOffererId: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 100 })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: false,
    })

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    const state = store.getState()
    expect(state.user.access).toBe('no-onboarding')
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.user.selectedVenue?.id).toBe(101)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)).toBe(
      '100'
    )
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '101'
    )
  })

  it('should set no-offerer when no offerers and no venues', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')
    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    expect(apiGetOffererSpy).not.toHaveBeenCalled()
    expect(apiGetVenueSpy).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.access).toBe('no-offerer')
  })

  it('should set unattached when getOfferer rejects with 403 on first-offerer path', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      name: 'ApiError',
      message: 'Forbidden',
      status: 403,
      body: {},
    })
    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    const store = configureTestStore()
    await store.dispatch(initializeUser(user)).unwrap()

    expect(apiGetVenueSpy).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.access).toBe('unattached')
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName?.id).toBe(100)
    expect(state.user.selectedVenue).toBeNull()

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)).toBe(
      '100'
    )
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should logout when getOfferer rejects with non-403 on venue path', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [makeVenueListItem({ id: 101, managingOffererId: 100 })],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 100 })
    )
    vi.spyOn(api, 'getOfferer').mockRejectedValue(
      new ApiError(
        { method: 'DELETE', url: '' },
        {} as unknown as ApiResult,
        'error'
      )
    )

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '100')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '101')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should dispatch logout when initialization fails before selection', async () => {
    const windowLocationReloadSpy = vi.fn()
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      reload: windowLocationReloadSpy,
    })
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(new Error())
    const logoutSpy = vi.spyOn(logoutModule, 'logout')
    vi.spyOn(api, 'signout').mockResolvedValue()

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '12')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '34')

    const store = configureTestStore()

    await store.dispatch(initializeUser(user)).unwrap()

    expect(logoutSpy).toHaveBeenCalledTimes(1)
    expect(windowLocationReloadSpy).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.user.access).toBeNull()
    expect(state.user.currentUser).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName).toBeNull()
    expect(state.offerer.offererNames).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    const configureStoreWithSwitchVenueFeature = () =>
      configureTestStore({
        features: {
          list: [{ id: 1, isActive: true, name: 'WIP_SWITCH_VENUE' }],
        },
      })

    it('should not select offerer when no saved venue id and return early', async () => {
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [
          makeVenueListItem({ id: 101, managingOffererId: 100 }),
          makeVenueListItem({ id: 201, managingOffererId: 200 }),
        ],
      })
      const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')
      const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

      const store = configureStoreWithSwitchVenueFeature()

      await store.dispatch(initializeUser(user)).unwrap()

      expect(apiGetOffererSpy).not.toHaveBeenCalled()
      expect(apiGetVenueSpy).not.toHaveBeenCalled()

      const state = store.getState()
      expect(state.user.access).toBeNull()
      expect(state.offerer.currentOfferer).toBeNull()
      expect(state.offerer.currentOffererName).toBeNull()
      expect(state.user.selectedVenue).toBeNull()
    })

    it('should not select offerer when saved venue id is not in venues list', async () => {
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [getOffererNameFactory({ id: 100 })],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [makeVenueListItem({ id: 101, managingOffererId: 100 })],
      })
      const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')
      const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '999')

      const store = configureStoreWithSwitchVenueFeature()

      await store.dispatch(initializeUser(user)).unwrap()

      expect(apiGetOffererSpy).not.toHaveBeenCalled()
      expect(apiGetVenueSpy).not.toHaveBeenCalled()

      const state = store.getState()
      expect(state.user.access).toBeNull()
      expect(state.offerer.currentOfferer).toBeNull()
      expect(state.offerer.currentOffererName).toBeNull()
      expect(state.user.selectedVenue).toBeNull()
    })

    it('should not select offerer when no offerers and no venues exist', async () => {
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')
      const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

      const store = configureStoreWithSwitchVenueFeature()

      await store.dispatch(initializeUser(user)).unwrap()

      expect(apiGetOffererSpy).not.toHaveBeenCalled()
      expect(apiGetVenueSpy).not.toHaveBeenCalled()

      const state = store.getState()
      expect(state.user.access).toBeNull()
      expect(state.offerer.currentOfferer).toBeNull()
      expect(state.offerer.currentOffererName).toBeNull()
      expect(state.user.selectedVenue).toBeNull()
    })
  })
})
