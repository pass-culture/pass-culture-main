import { render, screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'

import StoreProvider from '../StoreProvider'

vi.mock('apiClient/api', () => ({
  api: { getProfile: vi.fn() },
}))

const renderStoreProvider = () => {
  return render(
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
    vi.spyOn(api, 'getProfile').mockRejectedValue(undefined)
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
