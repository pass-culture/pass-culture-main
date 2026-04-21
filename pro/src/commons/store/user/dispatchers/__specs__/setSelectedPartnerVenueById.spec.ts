import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as handleErrorModule from '@/commons/errors/handleError'
import type { RootState } from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

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
    offerer: {
      currentOfferer: { ...defaultGetOffererResponseModel, id: 200 },
      currentOffererName: getOffererNameFactory({ id: 200 }),
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
    },
  }

  beforeEach(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '201')
  })

  it('should early-return when selecting the same venue', async () => {
    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({ nextSelectedPartnerVenueId: 201 })
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
        setSelectedPartnerVenueById({ nextSelectedPartnerVenueId: 101 })
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
        setSelectedPartnerVenueById({ nextSelectedPartnerVenueId: 101 })
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
        setSelectedPartnerVenueById({ nextSelectedPartnerVenueId: 301 })
      )
      .unwrap()

    expect(api.getVenue).toHaveBeenCalledTimes(0)
    expect(api.getOfferer).toHaveBeenCalledTimes(0)

    const state = store.getState()
    expect(state.user.access).toBe('unattached')
    expect(state.user.selectedPartnerVenue?.id).toBe(301)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '301'
    )
  })

  it('should handle unknown error without logging out (no APIError, no FrontendError)', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    vi.spyOn(api, 'getVenue').mockRejectedValue(new Error())
    const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')

    const store = configureTestStore(storeDataBase)

    await store
      .dispatch(
        setSelectedPartnerVenueById({ nextSelectedPartnerVenueId: 101 })
      )
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
    expect(state.user.selectedPartnerVenue?.id).toBe(201)

    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBe(
      '201'
    )
  })
})
