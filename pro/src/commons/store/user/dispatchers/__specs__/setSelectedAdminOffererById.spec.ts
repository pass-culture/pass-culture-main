import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as handleErrorModule from '@/commons/errors/handleError'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

import * as logoutModule from '../logout'
import { setSelectedAdminOffererById } from '../setSelectedAdminOffererById'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferer: vi.fn(),
    signout: vi.fn(),
  },
}))

vi.mock('@/commons/errors/handleError', () => ({
  handleError: vi.fn(),
}))

describe('setSelectedAdminOffererById', () => {
  describe('when called with an offerer ID', () => {
    it('should fetch the offerer and update the state', async () => {
      const offerer = {
        ...defaultGetOffererResponseModel,
        id: 100,
        name: 'Test Offerer',
      }
      vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)

      const store = configureTestStore({
        offerer: {
          offererNamesValidated: [getOffererNameFactory({ id: 100 })],
          currentOfferer: null,
          currentOffererName: null,
          offererNames: [getOffererNameFactory({ id: 100 })],
          offerersNamesWithPendingValidation: null,
        },
      })

      await store.dispatch(setSelectedAdminOffererById(100)).unwrap()

      expect(api.getOfferer).toHaveBeenCalledWith(100)

      const state = store.getState()
      expect(state.user.selectedAdminOfferer?.id).toBe(100)

      expect(
        localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
      ).toBe('100')
    })
  })

  describe('when called with an offerer object', () => {
    it('should use the provided offerer without fetching', async () => {
      const offerer = {
        ...defaultGetOffererResponseModel,
        id: 200,
        name: 'Provided Offerer',
      }
      const apiGetOffererSpy = vi.spyOn(api, 'getOfferer')

      const store = configureTestStore({
        offerer: {
          offererNamesValidated: [getOffererNameFactory({ id: 200 })],
          currentOfferer: null,
          currentOffererName: null,
          offererNames: [getOffererNameFactory({ id: 200 })],
          offerersNamesWithPendingValidation: null,
        },
      })

      await store.dispatch(setSelectedAdminOffererById(offerer)).unwrap()

      expect(apiGetOffererSpy).not.toHaveBeenCalled()

      const state = store.getState()
      expect(state.user.selectedAdminOfferer?.id).toBe(200)

      expect(
        localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
      ).toBe('200')
    })
  })

  describe('error handling', () => {
    it('should call handleError and logout on API error', async () => {
      vi.spyOn(console, 'error').mockImplementation(() => {})
      const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
      const logoutSpy = vi.spyOn(logoutModule, 'logout')
      vi.spyOn(api, 'getOfferer').mockRejectedValue({
        status: 500,
        message: 'Server Error',
        name: 'ApiError',
      })

      const store = configureTestStore({
        offerer: {
          offererNamesValidated: [getOffererNameFactory({ id: 100 })],
          currentOfferer: null,
          currentOffererName: null,
          offererNames: [getOffererNameFactory({ id: 100 })],
          offerersNamesWithPendingValidation: null,
        },
      })

      await store.dispatch(setSelectedAdminOffererById(100)).unwrap()

      expect(handleErrorSpy).toHaveBeenCalledWith(
        expect.objectContaining({ status: 500 }),
        "Une erreur est survenue lors du chargement de l'entité juridique."
      )
      expect(logoutSpy).toHaveBeenCalledTimes(1)
    })

    it('should not logout on non-API error', async () => {
      vi.spyOn(console, 'error').mockImplementation(() => {})
      const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
      const logoutSpy = vi.spyOn(logoutModule, 'logout')
      vi.spyOn(api, 'getOfferer').mockRejectedValue(new Error('Network error'))

      const store = configureTestStore({
        offerer: {
          offererNamesValidated: [getOffererNameFactory({ id: 100 })],
          currentOfferer: null,
          currentOffererName: null,
          offererNames: [getOffererNameFactory({ id: 100 })],
          offerersNamesWithPendingValidation: null,
        },
      })

      await store.dispatch(setSelectedAdminOffererById(100)).unwrap()

      expect(handleErrorSpy).toHaveBeenCalledWith(
        expect.any(Error),
        "Une erreur est survenue lors du chargement de l'entité juridique."
      )
      expect(logoutSpy).not.toHaveBeenCalled()
    })

    it('should create a minimal offerer without API call when offerer is not attached to display the banners', async () => {
      const handleErrorSpy = vi.spyOn(handleErrorModule, 'handleError')
      const getOffererSpy = vi.spyOn(api, 'getOfferer')

      const store = configureTestStore({
        offerer: {
          offererNamesValidated: [getOffererNameFactory({ id: 100 })],
          currentOfferer: null,
          currentOffererName: null,
          offererNames: [
            getOffererNameFactory({ id: 100 }),
            getOffererNameFactory({ id: 101 }),
          ],
          offerersNamesWithPendingValidation: [
            getOffererNameFactory({ id: 101 }),
          ],
        },
      })

      await store.dispatch(setSelectedAdminOffererById(101)).unwrap()

      expect(getOffererSpy).not.toHaveBeenCalled()

      expect(handleErrorSpy).not.toHaveBeenCalled()

      const state = store.getState()
      expect(state.user.selectedAdminOfferer?.id).toBe(101)

      expect(
        localStorage.getItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
      ).toBe('101')
    })
  })
})
