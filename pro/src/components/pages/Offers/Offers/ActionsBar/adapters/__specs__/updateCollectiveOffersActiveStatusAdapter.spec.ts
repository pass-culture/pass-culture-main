import * as pcapi from 'repository/pcapi/pcapi'

import { updateCollectiveOffersActiveStatusAdapter } from '../updateCollectiveOffersActiveStatusAdapter'

const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

describe('updateAllOffersActiveStatusAdapter', () => {
  it('should deactivate all offers and confirm', async () => {
    // given
    // @ts-ignore
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      status: 204,
    })

    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('2 offres ont bien été désactivées')
    expect(mockedPcapi.patchIsCollectiveOfferActive).toHaveBeenCalledWith(
      ['A1'],
      false
    )
    expect(mockedPcapi.patchIsTemplateOfferActive).toHaveBeenCalledWith(
      ['A1'],
      false
    )
  })

  it('should activate all offers and confirm', async () => {
    // given
    // @ts-ignore
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      status: 204,
    })

    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('2 offres ont bien été activées')
    expect(mockedPcapi.patchIsCollectiveOfferActive).toHaveBeenCalledWith(
      ['A1'],
      true
    )
    expect(mockedPcapi.patchIsTemplateOfferActive).toHaveBeenCalledWith(
      ['A1'],
      true
    )
  })

  it('should return an error when the update has failed', async () => {
    // given
    // @ts-ignore
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      status: 422,
    })

    // when
    const response = await updateCollectiveOffersActiveStatusAdapter({
      ids: ['T-A1', 'A1'],
      isActive: true,
    })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la désactivation des offres sélectionnées'
    )
  })
})
