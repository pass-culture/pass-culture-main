import * as pcapi from 'repository/pcapi/pcapi'

import { api } from 'apiClient/api'
import { updateCollectiveOffersActiveStatusAdapter } from '../updateCollectiveOffersActiveStatusAdapter'

describe('updateCollectiveOffersActiveStatusAdapter', () => {
  it('should deactivate all offers and confirm', async () => {
    // given
    jest
      .spyOn(pcapi, 'patchIsCollectiveOfferActive')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      // @ts-ignore
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('2 offres ont bien été désactivées')
    expect(pcapi.patchIsCollectiveOfferActive).toHaveBeenCalledWith(
      ['A1'],
      false
    )
    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledWith({
      ids: ['A1'],
      isActive: false,
    })
  })

  it('should activate all offers and confirm', async () => {
    // given
    jest
      .spyOn(pcapi, 'patchIsCollectiveOfferActive')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      // @ts-ignore
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('2 offres ont bien été activées')
    expect(pcapi.patchIsCollectiveOfferActive).toHaveBeenCalledWith(
      ['A1'],
      true
    )
    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledWith({
      ids: ['A1'],
      isActive: true,
    })
  })

  it('should return an error when the update has failed', async () => {
    // given
    jest.spyOn(pcapi, 'patchIsCollectiveOfferActive').mockRejectedValueOnce({
      status: 422,
    })
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      // @ts-ignore
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    // when
    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: false,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation des offres sélectionnées'
    )
  })
})
