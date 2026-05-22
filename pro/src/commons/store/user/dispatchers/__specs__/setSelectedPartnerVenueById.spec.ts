import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import { FrontendError } from '@/commons/errors/FrontendError'
import * as handleErrorModule from '@/commons/errors/handleError'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  makeGetVenueManagingOffererResponseModel,
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import * as logoutModule from '../logout'
import * as setSelectedAdminOffererByIdModule from '../setSelectedAdminOffererById'
import { setSelectedPartnerVenueById } from '../setSelectedPartnerVenueById'

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

describe('setSelectedPartnerVenueById', () => {
  const storeDataBase: Partial<RootState> = {
    user: {
      access: null,
      currentUser: null,
      selectedAdminOfferer: null,
      selectedPartnerVenue: makeGetVenueResponseModel({
        id: 201,
        managingOffererId: 200,
      }),
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 101,
          name: 'V1',
          managingOffererId: 100,
        }),
        makeVenueListItemLiteResponseModel({
          id: 201,
          name: 'V2',
          managingOffererId: 200,
        }),
        makeVenueListItemLiteResponseModel({
          id: 301,
          name: 'V3',
          managingOffererId: 300,
        }),
      ],
      venuesWithPendingValidation: [
        makeVenueListItemLiteResponseModel({
          id: 301,
          name: 'V3',
          managingOffererId: 300,
        }),
      ],
      offererNamesValidated: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
      ],
      offererNames: [
        getOffererNameFactory({ id: 100 }),
        getOffererNameFactory({ id: 200 }),
        getOffererNameFactory({ id: 300 }),
      ],
      offerersNamesWithPendingValidation: [getOffererNameFactory({ id: 300 })],
    },
  }

  beforeEach(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '201')
  })

  it('should early-return when selecting the same venue', async () => {
    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 201,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(api.getOfferer).not.toHaveBeenCalled()
    expect(api.getVenue).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.selectedPartnerVenue?.id).toBe(201)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '201'
    )
  })

  it('should compute nextSelectedPartnerVenue, fetch its offerer, update user access and persist it', async () => {
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
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.user.access).toBe('full')
    expect(state.user.selectedPartnerVenue?.id).toBe(101)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '101'
    )
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
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.user.access).toBe('no-onboarding')
    expect(state.user.selectedPartnerVenue?.id).toBe(101)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '101'
    )
  })

  it('should not call getVenue, getOfferer, and set access to unattached when offerer is not attached', async () => {
    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 301,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(0)
    expect(api.getOfferer).toHaveBeenCalledTimes(0)

    const state = store.getState()
    expect(state.user.access).toBe('unattached')
    expect(state.user.selectedPartnerVenue?.id).toBe(301)
    expect(state.user.selectedPartnerVenue?.managingOfferer?.id).toBe(300)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '301'
    )
  })

  it('should throw when offererNames is null', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    const logoutSpy = vi.spyOn(logoutModule, 'logout')

    const store = configureTestStore({
      ...storeDataBase,
      user: {
        offererNames: null,
      },
    })

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(console.error).toHaveBeenCalledWith(expect.any(FrontendError))
    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError),
      'Une erreur est survenue lors du changement de la structure.'
    )
    expect(logoutSpy).toHaveBeenCalledTimes(1)

    expect(api.getVenue).not.toHaveBeenCalled()
    expect(api.getOfferer).not.toHaveBeenCalled()

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should throw when nextSelectedOffererName is undefined', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 101, managingOffererId: 999 })
    )
    // The selected venue belongs to offerer 999, which is not in offererNamesValidated
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 999,
      isOnboarded: true,
    })
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    const logoutSpy = vi.spyOn(logoutModule, 'logout')

    const store = configureTestStore({
      user: {
        access: null,
        currentUser: null,
        selectedAdminOfferer: null,
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 201,
          managingOffererId: 200,
        }),
        venues: [
          makeVenueListItemLiteResponseModel({
            id: 101,
            managingOffererId: 999,
          }),
          makeVenueListItemLiteResponseModel({
            id: 201,
            managingOffererId: 200,
          }),
        ],
        venuesWithPendingValidation: null,
        offererNamesValidated: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
        offererNames: [
          getOffererNameFactory({ id: 100 }),
          getOffererNameFactory({ id: 200 }),
        ],
        offerersNamesWithPendingValidation: [],
      },
    })

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
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

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should align the selected admin offerer when shouldAlignSelectedAdminOfferer is true', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({ id: 100 }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })
    const setSelectedAdminOffererByIdSpy = vi.spyOn(
      setSelectedAdminOffererByIdModule,
      'setSelectedAdminOffererById'
    )

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: true,
        })
      )
      .unwrap()

    expect(setSelectedAdminOffererByIdSpy).toHaveBeenCalledExactlyOnceWith(100)
  })

  it('should not align the selected admin offerer when shouldAlignSelectedAdminOfferer is false', async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({ id: 100 }),
      })
    )
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
    })
    const setSelectedAdminOffererByIdSpy = vi.spyOn(
      setSelectedAdminOffererByIdModule,
      'setSelectedAdminOffererById'
    )

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 101,
          shouldAlignSelectedAdminOfferer: false,
        })
      )
      .unwrap()

    expect(setSelectedAdminOffererByIdSpy).not.toHaveBeenCalled()
  })

  it('should align the selected admin offerer with the synthetic managing offerer when the next venue is unattached', async () => {
    const setSelectedAdminOffererByIdSpy = vi.spyOn(
      setSelectedAdminOffererByIdModule,
      'setSelectedAdminOffererById'
    )

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 301,
          shouldAlignSelectedAdminOfferer: true,
        })
      )
      .unwrap()

    expect(api.getVenue).not.toHaveBeenCalled()
    expect(api.getOfferer).not.toHaveBeenCalled()
    expect(setSelectedAdminOffererByIdSpy).toHaveBeenCalledExactlyOnceWith(300)
  })

  it('should not align the selected admin offerer when early-returning on same venue selection', async () => {
    const setSelectedAdminOffererByIdSpy = vi.spyOn(
      setSelectedAdminOffererByIdModule,
      'setSelectedAdminOffererById'
    )

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({
          nextSelectedPartnerVenueId: 201,
          shouldAlignSelectedAdminOfferer: true,
        })
      )
      .unwrap()

    expect(setSelectedAdminOffererByIdSpy).not.toHaveBeenCalled()
  })

  describe('shouldRefresh', () => {
    it('should bypass the same-venue early-return and refetch venue + offerer when shouldRefresh is true', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValue(
        makeGetVenueResponseModel({
          id: 201,
          managingOfferer: makeGetVenueManagingOffererResponseModel({
            id: 200,
          }),
          isOnboarded: true,
        })
      )
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 200,
        isOnboarded: true,
      })

      const store = configureTestStore(storeDataBase)

      await store
        .dispatch(
          setSelectedPartnerVenueById({
            nextSelectedPartnerVenueId: 201,
            shouldAlignSelectedAdminOfferer: false,
            shouldRefresh: true,
          })
        )
        .unwrap()

      expect(api.getVenue).toHaveBeenCalledExactlyOnceWith(201)
      expect(api.getOfferer).toHaveBeenCalledExactlyOnceWith(200)

      const state = store.getState()
      expect(state.user.access).toBe('full')
      expect(state.user.selectedPartnerVenue?.id).toBe(201)
      expect(state.user.selectedPartnerVenue?.isOnboarded).toBe(true)
    })

    it('should realign the selected admin offerer when shouldRefresh is true and the refreshed venue belongs to the currently selected admin offerer', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValue(
        makeGetVenueResponseModel({
          id: 201,
          managingOfferer: makeGetVenueManagingOffererResponseModel({
            id: 200,
          }),
        })
      )
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 200,
        isOnboarded: true,
      })
      const setSelectedAdminOffererByIdSpy = vi.spyOn(
        setSelectedAdminOffererByIdModule,
        'setSelectedAdminOffererById'
      )

      const store = configureTestStore({
        ...storeDataBase,
        user: {
          ...storeDataBase.user!,
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            id: 200,
          },
        },
      })

      await store
        .dispatch(
          setSelectedPartnerVenueById({
            nextSelectedPartnerVenueId: 201,
            shouldAlignSelectedAdminOfferer: false,
            shouldRefresh: true,
          })
        )
        .unwrap()

      expect(setSelectedAdminOffererByIdSpy).toHaveBeenCalledExactlyOnceWith(
        200
      )
    })

    it('should not realign the selected admin offerer when shouldRefresh is true but the refreshed venue belongs to a different offerer than the selected admin offerer', async () => {
      vi.spyOn(api, 'getVenue').mockResolvedValue(
        makeGetVenueResponseModel({
          id: 201,
          managingOfferer: makeGetVenueManagingOffererResponseModel({
            id: 200,
          }),
        })
      )
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        id: 200,
        isOnboarded: true,
      })
      const setSelectedAdminOffererByIdSpy = vi.spyOn(
        setSelectedAdminOffererByIdModule,
        'setSelectedAdminOffererById'
      )

      const store = configureTestStore({
        ...storeDataBase,
        user: {
          ...storeDataBase.user!,
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            id: 100,
          },
        },
      })

      await store
        .dispatch(
          setSelectedPartnerVenueById({
            nextSelectedPartnerVenueId: 201,
            shouldAlignSelectedAdminOfferer: false,
            shouldRefresh: true,
          })
        )
        .unwrap()

      expect(setSelectedAdminOffererByIdSpy).not.toHaveBeenCalled()
    })
  })
})
