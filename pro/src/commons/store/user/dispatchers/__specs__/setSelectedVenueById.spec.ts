import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { FrontendError } from '@/commons/errors/FrontendError'
import * as handleErrorModule from '@/commons/errors/handleError'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import * as logoutModule from '../logout'
import { setSelectedVenueById } from '../setSelectedVenueById'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
    signout: vi.fn(),
  },
}))
vi.mock('@/commons/errors/handleError', () => ({
  handleError: vi.fn(),
}))

describe('setSelectedVenueById', () => {
  const storeDataBase: Partial<RootState> = {
    offerer: {
      currentOfferer: { ...defaultGetOffererResponseModel, id: 200 },
      currentOffererName: getOffererNameFactory({ id: 200 }),
      offererNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
      adminCurrentOfferer: null,
    },
    user: {
      access: null,
      currentUser: null,
      selectedVenue: makeGetVenueResponseModel({
        id: 201,
        managingOffererId: 200,
      }),
      venues: [
        makeVenueListItem({ id: 101, name: 'V1', managingOffererId: 100 }),
        makeVenueListItem({ id: 201, name: 'V2', managingOffererId: 200 }),
      ],
    },
  }

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '200')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '201')
  })

  it('should early-return when selecting the same venue', async () => {
    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 201 }))
      .unwrap()

    expect(api.getOfferer).not.toHaveBeenCalled()
    expect(api.getVenue).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('200')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('201')
  })

  it('should compute nextSelectedVenue, fetch its offerer, update user access and persist it', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 100 })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 101 }))
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(2)

    const state = store.getState()
    expect(state.user.access).toBe('full')
    expect(state.user.selectedVenue?.id).toBe(101)
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.offerer.currentOffererName?.id).toBe(100)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('100')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('101')
  })

  it('should set access to no-onboarding when offerer is not onboarded', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 100 })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: false,
    })

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 101 }))
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(2)

    const state = store.getState()
    expect(state.user.access).toBe('no-onboarding')
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.offerer.currentOffererName?.id).toBe(100)
    expect(state.user.selectedVenue?.id).toBe(101)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('100')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('101')
  })

  it('should throw when offererNames is null', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    const logoutSpy = vi.spyOn(logoutModule, 'logout')

    const store = configureTestStore({
      ...storeDataBase,
      offerer: {
        ...storeDataBase.offerer!,
        offererNames: null,
        adminCurrentOfferer: null,
      },
    })

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 101 }))
      .unwrap()

    expect(console.error).toHaveBeenCalledWith(expect.any(FrontendError))
    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError),
      'Une erreur est survenue lors du changement de la structure.'
    )
    expect(logoutSpy).toHaveBeenCalledTimes(1)

    expect(api.getVenue).not.toHaveBeenCalled()
    expect(api.getOfferer).not.toHaveBeenCalled()

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBeNull()
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('should throw when nextSelectedOffererName is undefined', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 999 })
    )
    // The selected venue belongs to offerer 999, which is not in offererNames
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 999,
      isOnboarded: true,
    })
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    const logoutSpy = vi.spyOn(logoutModule, 'logout')

    const store = configureTestStore({
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 200 },
        currentOffererName: getOffererNameFactory({ id: 200 }),
        offererNames: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
        adminCurrentOfferer: null,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: makeGetVenueResponseModel({
          id: 201,
          managingOffererId: 200,
        }),
        venues: [
          makeVenueListItem({ id: 101, managingOffererId: 999 }),
          makeVenueListItem({ id: 201, managingOffererId: 200 }),
        ],
      },
    })

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 101 }))
      .unwrap()

    expect(console.error).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError)
    )
    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError),
      'Une erreur est survenue lors du changement de la structure.'
    )
    expect(logoutSpy).toHaveBeenCalledTimes(1)

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBeNull()
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('should handle unknown error without logging out (no APIError, no FrontendError)', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    vi.spyOn(api, 'getVenue').mockRejectedValue(new Error())
    const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(setSelectedVenueById({ nextSelectedVenueId: 101 }))
      .unwrap()

    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(Error),
      'Une erreur est survenue lors du changement de la structure.'
    )

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(apiGetOffererSpy).not.toHaveBeenCalled()
    expect(api.signout).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.access).toBeNull()
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('200')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('201')
  })
})
