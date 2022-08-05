import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'

import StoreProvider from '../StoreProvider'

jest.mock('apiClient/api', () => ({
  api: { getProfile: jest.fn() },
}))

const renderStoreProvider = () => {
  return render(
    <StoreProvider>
      <p>Sub component</p>
    </StoreProvider>
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn(),
    listFeatures: jest.fn(),
  },
}))

describe('src | App', () => {
  beforeEach(() => {
    jest.spyOn(api, 'getProfile').mockRejectedValue(undefined)
    jest.spyOn(api, 'listFeatures').mockResolvedValue([])
  })
  it('should load current user', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.getProfile).toHaveBeenCalled()
  })
  it('should load features', async () => {
    await renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.listFeatures).toHaveBeenCalled()
  })
})
