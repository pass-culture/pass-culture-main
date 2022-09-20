import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import { patchIsCollectiveOfferActiveAdapter } from '../patchIsCollectiveOfferActiveAdapter'

describe('patchIsOfferActiveCollectiveAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
    const response = await patchIsCollectiveOfferActiveAdapter({
      offerId: '',
      isActive: false,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation de votre offre. L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should return an error when the update has failed', async () => {
    // given
    jest
      .spyOn(api, 'patchCollectiveOffersActiveStatus')
      .mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 422 } as ApiResult, '')
      )

    // when
    const response = await patchIsCollectiveOfferActiveAdapter({
      offerId: '12',
      isActive: false,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation de votre offre. '
    )
  })
  it('should confirm when the offer was activated', async () => {
    // given
    jest.spyOn(api, 'patchCollectiveOffersActiveStatus').mockResolvedValueOnce()

    // when
    const response = await patchIsCollectiveOfferActiveAdapter({
      offerId: '12',
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Votre offre est maintenant inactive et sera invisible pour les utilisateurs d’ADAGE.'
    )
  })
  it('should confirm when the offer was deactivated', async () => {
    // given
    jest.spyOn(api, 'patchCollectiveOffersActiveStatus').mockResolvedValueOnce()

    // when
    const response = await patchIsCollectiveOfferActiveAdapter({
      offerId: '12',
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Votre offre est maintenant active et visible dans ADAGE.'
    )
  })
})
