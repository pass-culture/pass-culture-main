import { api } from 'apiClient/api'
import { configureTestStore } from 'commons/store/testUtils'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'

import { initializeUserThunk } from '../thunks'

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

vi.mock('commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn().mockReturnValue(true),
}))

describe('initializeUserThunk', () => {
  const mockUser = sharedCurrentUserFactory()

  const mockOfferers = {
    offerersNames: [getOffererNameFactory()],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should dispatch updateUser when all API calls succeed', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue(mockOfferers)
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    const store = configureTestStore()

    await store.dispatch(initializeUserThunk(mockUser))

    expect(store.getState().user.currentUser).toEqual(mockUser)
  })

  it('should dispatch all update functions with null and reject when API call fails', async () => {
    const mockError = new Error('API Error')
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(mockError)
    const store = configureTestStore()

    const result = await store.dispatch(initializeUserThunk(mockUser))

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()

    expect(result).toEqual({
      error: { message: 'Rejected' },
      type: 'user/initialize/rejected',
      payload: { error: 'UNKNOWN_ERROR' },
      meta: {
        aborted: false,
        condition: false,
        arg: mockUser,
        requestStatus: 'rejected',
        requestId: expect.any(String),
        rejectedWithValue: true,
      },
    })
  })

  it('should handle getOfferer error and continue if status is 403', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue(mockOfferers)
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      status: 403,
      body: { error: 'Forbidden' },
    })
    const store = configureTestStore()

    await store.dispatch(initializeUserThunk(mockUser))

    expect(store.getState().user.currentUser).toBeNull()
  })

  it('should handle getOfferer error and reject if status is not 403', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue(mockOfferers)
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      status: 500,
      body: { error: 'Internal Server Error' },
    })
    const store = configureTestStore()

    const result = await store.dispatch(initializeUserThunk(mockUser))

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()

    expect(result).toEqual({
      error: { message: 'Rejected' },
      type: 'user/initialize/rejected',
      payload: { error: 'UNKNOWN_ERROR' },
      meta: {
        aborted: false,
        condition: false,
        arg: mockUser,
        requestStatus: 'rejected',
        requestId: expect.any(String),
        rejectedWithValue: true,
      },
    })
  })

  it('should handle ApiError and reject with proper error format', async () => {
    const mockApiError = {
      status: 403,
      name: 'ApiError',
      message: 'Bad Request',
    }
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(mockApiError)
    const store = configureTestStore()

    const result = await store.dispatch(initializeUserThunk(mockUser))

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()

    expect(result).toEqual({
      error: { message: 'Rejected' },
      type: 'user/initialize/rejected',
      payload: {
        error: 'API_ERROR',
        status: 403,
        body: 'Bad Request',
      },
      meta: {
        aborted: false,
        condition: false,
        arg: mockUser,
        requestStatus: 'rejected',
        requestId: expect.any(String),
        rejectedWithValue: true,
      },
    })
  })
})
