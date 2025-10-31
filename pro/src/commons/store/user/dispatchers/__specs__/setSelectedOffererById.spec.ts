import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '@/commons/core/shared/constants'
import { FrontendError } from '@/commons/errors/FrontendError'
import * as handleErrorModule from '@/commons/errors/handleError'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'

import { setSelectedOffererById } from '../setSelectedOffererById'

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
}))
vi.mock('@/commons/errors/handleError', () => ({
  handleError: vi.fn(),
}))

describe('setSelectedOffererById', () => {
  const currentOffererBase = { ...defaultGetOffererResponseModel, id: 100 }
  const currentOffererNameBase = getOffererNameFactory({ id: 100 })
  const selectedVenueBase = makeVenueListItem({
    id: 101,
    managingOffererId: 100,
  })
  const offerersNamesResponseBase = {
    offerersNames: [
      getOffererNameFactory({ id: 100 }),
      getOffererNameFactory({ id: 200 }),
    ],
  }
  const venuesBase = [
    makeVenueListItem({ id: 101, managingOffererId: 100 }),
    makeVenueListItem({ id: 102, managingOffererId: 100 }),
    makeVenueListItem({ id: 201, managingOffererId: 200 }),
  ]

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  it('should early-return when nextCurrentOffererId equals previous currentOfferer id', async () => {
    localStorage.setItem(SAVED_OFFERER_ID_KEY, '100')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '101')

    const store = configureTestStore({
      offerer: {
        currentOfferer: currentOffererBase,
        currentOffererName: currentOffererNameBase,
        offererNames: offerersNamesResponseBase.offerersNames,
      },
      user: {
        currentUser: null,
        access: null,
        selectedVenue: selectedVenueBase,
        venues: venuesBase,
      },
    })

    const result = await store
      .dispatch(setSelectedOffererById({ nextSelectedOffererId: 100 }))
      .unwrap()

    expect(result).toBeNull()

    expect(api.getOfferer).not.toHaveBeenCalled()
    expect(api.getVenues).not.toHaveBeenCalled()
    expect(api.listOfferersNames).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.offerer.currentOffererName?.id).toBe(100)
    expect(state.user.selectedVenue?.id).toBe(101)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('100')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('101')
  })

  it('should refetch offerers/venues, set access, currentOfferer, selectedVenue and persist ids', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: false,
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: venuesBase,
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue(
      offerersNamesResponseBase
    )

    const store = configureTestStore({
      offerer: {
        currentOfferer: null,
        currentOffererName: null,
        offererNames: null,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: null,
        venues: [],
      },
    })

    const result = await store
      .dispatch(
        setSelectedOffererById({
          nextSelectedOffererId: 100,
          shouldRefetch: true,
        })
      )
      .unwrap()

    expect(result).toBe('no-onboarding')

    expect(api.getVenues).toHaveBeenCalledTimes(1)
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.offerer.offererNames).toEqual(
      offerersNamesResponseBase.offerersNames
    )
    expect(state.user.access).toBe('no-onboarding')
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.offerer.currentOffererName?.id).toBe(100)
    expect(state.user.selectedVenue?.id).toBe(101)
    expect(state.user.venues).toEqual(venuesBase)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('100')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('101')
  })

  it('should use existing venues when shouldRefetch=false and set access to full', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 200,
      isOnboarded: true,
    })

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '100')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '101')

    const store = configureTestStore({
      offerer: {
        currentOfferer: currentOffererBase,
        currentOffererName: currentOffererNameBase,
        offererNames: offerersNamesResponseBase.offerersNames,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: selectedVenueBase,
        venues: venuesBase,
      },
    })

    const getVenuesSpy = vi.spyOn(api, 'getVenues')
    const listOfferersNamesSpy = vi.spyOn(api, 'listOfferersNames')

    const result = await store
      .dispatch(setSelectedOffererById({ nextSelectedOffererId: 200 }))
      .unwrap()

    expect(result).toBe('full')

    const state = store.getState()
    expect(getVenuesSpy).not.toHaveBeenCalled()
    expect(listOfferersNamesSpy).not.toHaveBeenCalled()
    expect(state.offerer.currentOfferer?.id).toBe(200)
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue?.id).toBe(201)
    expect(state.user.access).toBe('full')

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('200')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('201')
  })

  it('should set access to unattached on 403 ApiError and not throw', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      name: 'ApiError',
      message: 'Forbidden',
      status: 403,
      body: {},
    })

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '100')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '101')

    const store = configureTestStore({
      offerer: {
        currentOfferer: currentOffererBase,
        currentOffererName: currentOffererNameBase,
        offererNames: offerersNamesResponseBase.offerersNames,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: selectedVenueBase,
        venues: venuesBase,
      },
    })

    const result = await store
      .dispatch(setSelectedOffererById({ nextSelectedOffererId: 200 }))
      .unwrap()

    expect(result).toBe('unattached')

    expect(api.getOfferer).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.user.access).toBe('unattached')
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName?.id).toBe(200)
    expect(state.user.selectedVenue).toBeNull()

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('200')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('should throw when no venue matches the offerer', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 100,
      isOnboarded: true,
      name: 'O',
    })
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '100')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '101')

    const store = configureTestStore({
      offerer: {
        currentOfferer: currentOffererBase,
        currentOffererName: currentOffererNameBase,
        offererNames: offerersNamesResponseBase.offerersNames,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: selectedVenueBase,
        venues: venuesBase,
      },
    })

    const result = await store
      .dispatch(setSelectedOffererById({ nextSelectedOffererId: 900 }))
      .unwrap()

    expect(result).toBeNull()

    expect(console.error).toHaveBeenCalledWith(expect.any(FrontendError))
    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError),
      'Une erreur est survenue lors du changement de la structure.'
    )

    const state = store.getState()
    expect(state.user.access).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBeNull()
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBeNull()
  })

  it('should handle unknown error without logging out', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
    vi.spyOn(api, 'getOfferer').mockRejectedValue(new Error())

    localStorage.setItem(SAVED_OFFERER_ID_KEY, '100')
    localStorage.setItem(SAVED_VENUE_ID_KEY, '101')

    const store = configureTestStore({
      offerer: {
        currentOfferer: currentOffererBase,
        currentOffererName: currentOffererNameBase,
        offererNames: offerersNamesResponseBase.offerersNames,
      },
      user: {
        access: null,
        currentUser: null,
        selectedVenue: selectedVenueBase,
        venues: venuesBase,
      },
    })

    const result = await store
      .dispatch(setSelectedOffererById({ nextSelectedOffererId: 200 }))
      .unwrap()

    expect(result).toBeNull()
    expect(handleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(Error),
      'Une erreur est survenue lors du changement de la structure.'
    )

    expect(api.signout).not.toHaveBeenCalled()

    const state = store.getState()
    expect(state.user.access).toBeNull()
    expect(state.offerer.currentOfferer?.id).toBe(100)
    expect(state.offerer.currentOffererName?.id).toBe(100)
    expect(state.user.selectedVenue?.id).toBe(101)

    expect(localStorage.getItem(SAVED_OFFERER_ID_KEY)).toBe('100')
    expect(localStorage.getItem(SAVED_VENUE_ID_KEY)).toBe('101')
  })
})
