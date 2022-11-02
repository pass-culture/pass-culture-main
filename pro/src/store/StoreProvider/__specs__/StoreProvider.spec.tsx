import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { SharedCurrentUserResponseModel } from 'apiClient/v1'

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
    listOfferersNames: jest.fn(),
  },
}))

describe('src | App', () => {
  beforeEach(() => {
    jest
      .spyOn(api, 'getProfile')
      .mockResolvedValue({} as SharedCurrentUserResponseModel)
    jest.spyOn(api, 'listFeatures').mockResolvedValue([])
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [] })
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
  it('should load offerersNames', async () => {
    renderStoreProvider()
    await screen.findByText('Sub component')

    // Then
    expect(api.listOfferersNames).toHaveBeenCalled()
  })
  describe('failing', () => {
    beforeEach(() => {
      jest.spyOn(api, 'getProfile').mockRejectedValue(undefined)
      jest.spyOn(api, 'listFeatures').mockRejectedValue(undefined)
      jest.spyOn(api, 'listOfferersNames').mockRejectedValue(undefined)
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
    it('should load offerersNames', async () => {
      renderStoreProvider()
      await screen.findByText('Sub component')

      // Then
      expect(api.listOfferersNames).toHaveBeenCalled()
    })
  })
})
