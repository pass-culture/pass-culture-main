import { api } from '@/apiClient/api'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'

import { configureTestStore } from '../../../testUtils'
import { initializeUser } from '../initializeUser'

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    getVenues: vi.fn(),
    signout: vi.fn(),
  },
}))

vi.mock('@/commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn().mockReturnValue(true),
}))

describe('initializeUser', () => {
  const sharedCurrentUser = sharedCurrentUserFactory()

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Offerer A',
        }),
      ],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        makeVenueListItem({
          id: 2,
          managingOffererId: 1,
          name: 'Venue A1',
        }),
      ],
    })
  })

  it('should dispatch updateUser when all API calls succeed', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Offerer A',
    })
    const store = configureTestStore()

    await store.dispatch(initializeUser(sharedCurrentUser))

    expect(store.getState().user.currentUser).toEqual(sharedCurrentUser)
  })

  it('should dispatch all update functions with null and reject when API call fails', async () => {
    const mockError = new Error('API Error')
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(mockError)
    const store = configureTestStore()

    await store.dispatch(initializeUser(sharedCurrentUser))

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().user.selectedVenue).toBeNull()
    expect(store.getState().user.venues).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()
  })

  it('should handle getOfferer error and continue if status is 403', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      status: 403,
      body: { error: 'Forbidden' },
    })
    const store = configureTestStore()

    await store.dispatch(initializeUser(sharedCurrentUser))

    expect(store.getState().user.currentUser).toBeNull()
  })

  it('should handle getOfferer error and reject if status is not 403', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValue({
      status: 500,
      body: { error: 'Internal Server Error' },
    })
    const store = configureTestStore()

    await initializeUser(sharedCurrentUser)

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().user.selectedVenue).toBeNull()
    expect(store.getState().user.venues).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()
  })

  it('should handle ApiError by logging user out', async () => {
    const mockApiError = {
      status: 403,
      name: 'ApiError',
      message: 'Bad Request',
    }
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue(mockApiError)
    const store = configureTestStore()

    await store.dispatch(initializeUser(sharedCurrentUser))

    expect(store.getState().user.currentUser).toBeNull()
    expect(store.getState().user.selectedVenue).toBeNull()
    expect(store.getState().user.venues).toBeNull()
    expect(store.getState().offerer.offererNames).toBeNull()
    expect(store.getState().offerer.currentOfferer).toBeNull()
  })
})
