import { vi } from 'vitest'

import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api, apiNew } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  makeGetVenueManagingOffererResponseModel,
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import { initializeUser } from '../initializeUser'
import * as logoutModule from '../logout'

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getVenue: vi.fn(),
    getVenuesLite: vi.fn(),
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
  apiNew: {
    listOfferersNames: vi.fn(),
  },
}))

describe('initializeUser', () => {
  const user = sharedCurrentUserFactory({ email: 'user@pro.fr', id: 1 })

  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    window.history.pushState({}, '', '/')
  })

  it('should use saved venue id from localStorage when present and valid', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 102,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 100,
        }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '101')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(101)
    expect(state.user.selectedAdminOfferer?.id).toBe(100)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '101'
    )
  })

  it('should auto-select venue when user has only one venue', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 100,
        }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(101)
  })

  it('should return early without selection when user has multiple venues and no localStorage selection', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 102,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    expect(apiGetVenueSpy).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue).toBeNull()
  })

  it('should return early without selection when user has no venues', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    expect(apiGetVenueSpy).not.toHaveBeenCalled()
  })

  it('should return early without selection when no offerers and no venues', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [],
      venuesWithPendingValidation: [],
    })
    const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')
    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID, '999')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    expect(apiGetOffererSpy).not.toHaveBeenCalled()
    expect(apiGetVenueSpy).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.selectedAdminOfferer).toBeNull()
    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
    ).toBeNull()
  })

  it('should auto-select single venue and set admin offerer when newOffererId is provided', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 100,
        }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const store = configureTestStore()

    await store.dispatch(initializeUser({ newOffererId: 100, user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(101)
    expect(state.user.selectedAdminOfferer?.id).toBe(100)
  })

  it('should unset venue and set admin offerer when newOffererId has multiple venues', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 102,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    const apiGetVenueSpy = vi.spyOn(api, 'getVenue')

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '101')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ newOffererId: 100, user })).unwrap()

    expect(apiGetVenueSpy).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue).toBeNull()
    expect(state.user.selectedAdminOfferer?.id).toBe(100)
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should set admin offerer from newOffererId even when venue is not selected', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 200,
      isOnboarded: false,
    })

    const store = configureTestStore()

    await store.dispatch(initializeUser({ newOffererId: 200, user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue).toBeNull()
    expect(state.user.selectedAdminOfferer?.id).toBe(200)
  })

  it('should ignore invalid venue id from localStorage and return early', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 102,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '999')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue).toBeNull()
  })

  it('should get the venue id from URL params for backoffice switcher', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 201,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 201,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 100,
        }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })

    window.history.pushState({}, '', '/?venue=201')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(201)
  })

  it('should keep the admin offerer from localStorage independently from the partner venue selection', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({ id: 100 }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockImplementation(
      (offererId: number) =>
        Promise.resolve({
          ...defaultGetOffererResponseModel,
          id: offererId,
          isOnboarded: true,
        }) as ReturnType<typeof api.getOfferer>
    )

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID, '200')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(101)
    expect(state.user.selectedAdminOfferer?.id).toBe(200)
    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
    ).toBe('200')
  })
})

describe('error handling', () => {
  const user = sharedCurrentUserFactory({ email: 'user@pro.fr', id: 1 })

  it('should logout when getOfferer rejects with non-403 error', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(apiNew, 'listOfferersNames').mockResolvedValue({
      offerersNames: [getOffererNameFactory({ id: 100 })],
    })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          managingOffererId: 100,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 100,
        }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockRejectedValue(
      new ApiError(
        { method: 'DELETE', url: '' },
        {} as unknown as ApiResult,
        'error'
      )
    )

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '101')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should dispatch logout when initialization fails before selection', async () => {
    vi.spyOn(apiNew, 'listOfferersNames').mockRejectedValue(new Error())
    const logoutSpy = vi.spyOn(logoutModule, 'logout')
    vi.spyOn(api, 'signout').mockResolvedValue()

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '34')

    const store = configureTestStore()

    await store.dispatch(initializeUser({ user })).unwrap()

    expect(logoutSpy).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.user.currentUser).toBeNull()
    expect(state.user.selectedAdminOfferer).toBeNull()
    expect(state.user.offererNames).toBeNull()
    expect(state.user.selectedPartnerVenue).toBeNull()
    expect(state.user.venues).toBeNull()

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })
})
