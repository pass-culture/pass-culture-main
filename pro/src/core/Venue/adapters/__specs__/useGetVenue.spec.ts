import { renderHook } from '@testing-library/react-hooks'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'

import { useGetVenue } from '../getVenueAdapter'

describe('useGetVenue', () => {
  it('should return loading payload then success payload', async () => {
    const apiVenue: GetVenueResponseModel = {
      bannerMeta: {
        image_credit: null,
        original_image_url:
          'http://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'http://localhost/storage/thumbs/venues/CU_1661432577',
      collectiveDomains: [],
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        website: 'http://test.com',
      },
      dateCreated: '2022-07-29T12:18:43.087097Z',
      fieldsUpdated: [],
      id: 'AE',
      isValidated: true,
      isVirtual: false,
      isPermanent: true,
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
      publicName: 'Cinéma des iles',
    }

    jest.spyOn(api, 'getVenue').mockResolvedValue(apiVenue)

    const { result, waitForNextUpdate } = renderHook(() => useGetVenue('AE'))
    const loadingState = result.current

    expect(loadingState.data).toBeUndefined()
    expect(loadingState.isLoading).toBe(true)
    expect(loadingState.error).toBeUndefined()

    const venue = {
      bannerMeta: {
        image_credit: null,
        original_image_url:
          'http://localhost/storage/thumbs/venues/CU_1661432578',
        crop_params: {
          x_crop_percent: 0.005169172932330823,
          y_crop_percent: 0,
          height_crop_percent: 1,
          width_crop_percent: 0.9896616541353384,
        },
      },
      bannerUrl: 'http://localhost/storage/thumbs/venues/CU_1661432577',
      contact: {
        email: 'test@test.com',
        phoneNumber: '0606060606',
        webSite: 'http://test.com',
      },
      id: 'AE',
      isPermanent: true,
      publicName: 'Cinéma des iles',
    }

    await waitForNextUpdate()
    expect(api.getVenue).toHaveBeenCalledWith('AE')
    const updatedState = result.current
    expect(updatedState.isLoading).toBe(false)
    expect(updatedState.data).toEqual(venue)
    expect(updatedState.error).toBeUndefined()
  })
})
