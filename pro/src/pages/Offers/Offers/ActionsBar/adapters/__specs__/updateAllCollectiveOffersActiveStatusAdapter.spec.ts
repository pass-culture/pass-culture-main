import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { updateAllCollectiveOffersActiveStatusAdapter } from '../updateAllCollectiveOffersActiveStatusAdapter'

describe('updateAllCollectiveOffersActiveStatusAdapter', () => {
  it('should deactivate all collective offers and confirm', async () => {
    // given
    jest
      .spyOn(api, 'patchAllCollectiveOffersActiveStatus')
      .mockResolvedValueOnce()

    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: false },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    )
  })

  it('should activate all collective offers and confirm', async () => {
    // given
    jest
      .spyOn(api, 'patchAllCollectiveOffersActiveStatus')
      .mockResolvedValueOnce()

    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: true },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Les offres sont en cours d’activation, veuillez rafraichir dans quelques instants'
    )
  })

  it('should return an error when the update has failed', async () => {
    // given
    // @ts-ignore
    jest
      .spyOn(api, 'patchAllCollectiveOffersActiveStatus')
      .mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          { body: { status: 422 } } as ApiResult,
          ''
        )
      )

    // when
    const response = await updateAllCollectiveOffersActiveStatusAdapter({
      searchFilters: { isActive: false },
      nbSelectedOffers: 10,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation des offres'
    )
  })
})
