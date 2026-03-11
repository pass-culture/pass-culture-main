import { screen } from '@testing-library/react'

import { api, apiNew } from '@/apiClient/api'
import { UserRole } from '@/apiClient/v1'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  makeGetVenueResponseModel,
  makeVenueListItemLiteResponseModel,
} from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StoreProvider } from '../StoreProvider'

const renderStoreProvider = () => {
  return renderWithProviders(
    <StoreProvider>
      <p>Sub component</p>
    </StoreProvider>
  )
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
    getVenuesLite: vi.fn(),
  },
  apiNew: {
    listFeatures: vi.fn(),
  },
}))
vi.mock('@/commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn().mockReturnValue(true),
}))

describe('src | App', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getProfile').mockResolvedValue({
      id: 1,
      email: 'email@example.com',
      roles: [UserRole.ADMIN],
      isEmailValidated: true,
      dateCreated: '2022-07-29T12:18:43.087097Z',
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 1,
      name: 'Offerer A',
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({
        id: 2,
        managingOffererId: 1,
        name: 'Venue A1',
      })
    )
    const mockOffererNames = {
      offerersNames: [{ id: 1, name: 'Offerer A' }],
      offerersNamesWithPendingValidation: [],
    }
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue(mockOffererNames)
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 2,
          managingOffererId: 1,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(apiNew, 'listFeatures').mockResolvedValue([])
  })

  it('should load current user, its offerers and', async () => {
    renderStoreProvider()

    await screen.findByText('Sub component')

    expect(apiNew.listFeatures).toHaveBeenCalledTimes(1)
    expect(api.getProfile).toHaveBeenCalledTimes(1)
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.getVenuesLite).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)
    expect(api.getVenue).toHaveBeenCalledTimes(1)
  })
})
