import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as handleErrorModule from '@/commons/errors/handleError'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import { logout } from '../logout'

vi.mock('@/apiClient/api', () => ({
  api: {
    signout: vi.fn(),
  },
}))
vi.mock('@/commons/errors/handleError', () => ({
  handleError: vi.fn(),
}))

describe('logout', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()

    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID, '1')
    localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '2')
  })

  it('should call signout, clear localStorage, and reset related slices when shouldCallSignout=true', async () => {
    const store = configureTestStore({
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
        currentOffererName: getOffererNameFactory({ id: 1 }),
        offererNames: [getOffererNameFactory({ id: 1 })],
      },
      user: {
        access: 'full',
        currentUser: sharedCurrentUserFactory({ id: 3 }),
        selectedVenue: makeVenueListItem({ id: 2 }),
        venues: [makeVenueListItem({ id: 2 })],
      },
    })

    await store.dispatch(logout()).unwrap()

    expect(api.signout).toHaveBeenCalledTimes(1)

    const state = store.getState()
    expect(state.offerer.offererNames).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName).toBeNull()
    expect(state.user.currentUser).toBeNull()
    expect(state.user.access).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })

  it('should handle signout error gracefully and still reset state', async () => {
    vi.spyOn(api, 'signout').mockRejectedValue(new Error())
    const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')

    const store = configureTestStore()

    await store.dispatch(logout()).unwrap()

    expect(handleErrorSpy).toHaveBeenCalledWith(
      expect.any(Error),
      'Une erreur est survenue lors de la déconnexion.'
    )

    const state = store.getState()
    expect(state.offerer.offererNames).toBeNull()
    expect(state.offerer.currentOfferer).toBeNull()
    expect(state.offerer.currentOffererName).toBeNull()
    expect(state.user.currentUser).toBeNull()
    expect(state.user.access).toBeNull()
    expect(state.user.selectedVenue).toBeNull()
    expect(state.user.venues).toBeNull()

    expect(
      localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    ).toBeNull()
    expect(localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)).toBeNull()
  })
})
