import { api } from 'apiClient/api'

import { patchIsTemplateOfferActiveAdapter } from '../patchIsTemplateOfferActiveAdapter'

describe('patchIsTemplateOfferActiveAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
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
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockRejectedValue({})

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
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
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockResolvedValue()

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
      offerId: '12',
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Votre offre est désactivée et n’est plus visible sur ADAGE'
    )
  })
  it('should confirm when the offer was deactivated', async () => {
    // given
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockResolvedValue()

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
      offerId: '12',
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(
      'Votre offre est maintenant active et visible dans ADAGE'
    )
  })
})
