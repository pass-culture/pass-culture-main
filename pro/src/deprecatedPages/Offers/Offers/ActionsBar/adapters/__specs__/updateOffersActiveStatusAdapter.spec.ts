import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { updateOffersActiveStatusAdapter } from '../updateOffersActiveStatusAdapter'

describe('updateOffersActiveStatusAdapter', () => {
  it('should deactivate all offers and confirm', async () => {
    // given
    jest.spyOn(api, 'patchOffersActiveStatus').mockResolvedValueOnce()

    const response = await updateOffersActiveStatusAdapter({
      ids: ['A1', 'A2', 'A3'],
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('3 offres ont bien été désactivées')
  })

  it('should publish all offers and confirm', async () => {
    // given
    jest.spyOn(api, 'patchOffersActiveStatus').mockResolvedValueOnce()

    const response = await updateOffersActiveStatusAdapter({
      ids: ['A1', 'A2', 'A3'],
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('3 offres ont bien été publiées')
  })

  it('should return an error when the update has failed', async () => {
    // given
    jest
      .spyOn(api, 'patchOffersActiveStatus')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 422 } as ApiResult, '')
      )

    // when
    const response = await updateOffersActiveStatusAdapter({
      ids: ['A1', 'A2', 'A3'],
      isActive: false,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation des offres sélectionnées'
    )
  })
})
