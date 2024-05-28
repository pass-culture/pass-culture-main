import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import { StoreProvider } from '../StoreProvider'

const renderStoreProvider = () => {
  return renderWithProviders(
    <StoreProvider>
      <p>Sub component</p>
    </StoreProvider>
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    listFeatures: vi.fn(),
  },
}))

describe('src | App', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getProfile').mockResolvedValue({
      id: 1,
      email: 'email@example.com',
      isAdmin: true,
      roles: [UserRole.ADMIN],
      isEmailValidated: true,
      dateCreated: '2022-07-29T12:18:43.087097Z',
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
})
