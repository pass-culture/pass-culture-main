import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { UserRole } from '@/apiClient/v1'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
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
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
    getVenues: vi.fn(),
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
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })

  it('should load current user, its offerers and', async () => {
    renderStoreProvider()

    await screen.findByText('Sub component')

    expect(api.listFeatures).toHaveBeenCalled()
    expect(api.getProfile).toHaveBeenCalled()
    expect(api.listOfferersNames).toHaveBeenCalled()
    expect(api.getVenues).toHaveBeenCalled()
    expect(api.getOfferer).toHaveBeenCalled()
  })
})
