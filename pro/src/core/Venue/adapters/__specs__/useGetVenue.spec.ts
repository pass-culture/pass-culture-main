import { renderHook } from '@testing-library/react-hooks'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'

import { useGetVenue } from '../getVenueAdapter'

describe('useGetVenue', () => {
  it('should return loading payload then success payload', async () => {
    const apiVenue: GetVenueResponseModel = {
      publicName: 'Cinéma des iles',
      collectiveDomains: [],
      dateCreated: '2022-07-29T12:18:43.087097Z',
      fieldsUpdated: [],
      id: 'AE',
      isValidated: true,
      isVirtual: false,
      managingOfferer: {
        city: 'Paris',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        fieldsUpdated: [],
        id: 'AA',
        isValidated: true,
        name: 'Test structure name',
        postalCode: '75001',
      },
      managingOffererId: 'AA',
      name: 'Lieu name',
      nonHumanizedId: 12,
    }

    jest.spyOn(api, 'getVenue').mockResolvedValue(apiVenue)

    const { result, waitForNextUpdate } = renderHook(() => useGetVenue('AE'))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const venue = { publicName: 'Cinéma des iles' }

    await waitForNextUpdate()
    expect(api.getVenue).toHaveBeenCalledWith('AE')
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual(venue)
    expect(updatedState.error).toBeUndefined()
  })
})
