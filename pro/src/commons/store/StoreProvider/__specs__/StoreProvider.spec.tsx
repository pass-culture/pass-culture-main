import { screen } from '@testing-library/react'

import { api } from '@/apiClient//api'
import { UserRole } from '@/apiClient//v1'
import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { StoreProvider } from '../StoreProvider'

const renderStoreProvider = () => {
  return renderWithProviders(
    <StoreProvider>
      <p>Sub component</p>
    </StoreProvider>
  )
}

vi.mock('@/apiClient//api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

describe('src | App', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getProfile').mockResolvedValue({
      id: 1,
      email: 'email@example.com',
      isAdmin: false,
      roles: [UserRole.ADMIN],
      isEmailValidated: true,
      dateCreated: '2022-07-29T12:18:43.087097Z',
    })
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Ma super structure',
        }),
      ],
    })
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })
  it('should load current user', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.getProfile).toHaveBeenCalled()
  })
  it('should load features', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.listFeatures).toHaveBeenCalled()
  })
  it('should load offerer names', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.listOfferersNames).toHaveBeenCalled()
  })

  it('should load offerer', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    expect(api.getOfferer).toHaveBeenCalled()
  })
})
