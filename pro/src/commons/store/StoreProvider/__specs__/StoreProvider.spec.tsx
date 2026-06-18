import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
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
    getVenue: vi.fn(),
    getVenuesLite: vi.fn(),
    getOfferer: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
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
    const offerersNames = [{ id: 1, name: 'Offerer A', validated: true }]
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames })
    vi.spyOn(api, 'getVenuesLite').mockResolvedValue({
      venues: [
        makeVenueListItemLiteResponseModel({
          id: 2,
          managingOffererId: 1,
        }),
      ],
      venuesWithPendingValidation: [],
    })
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })

  it('should load current user, its offerers and venues', async () => {
    renderStoreProvider()

    await screen.findByText('Sub component')

    expect(api.listFeatures).toHaveBeenCalledTimes(1)
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.getProfile).toHaveBeenCalledTimes(1)
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.getVenuesLite).toHaveBeenCalledTimes(1)
    // TODO (igabriele, 2026-05-11): Change back to `1` once `nextSelectedPartnerVenue` is removed from `setSelectedPartnerVenueById` (`WIP_SWITCH_VENUE`).
    expect(api.getVenue).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(2)
  })
})
