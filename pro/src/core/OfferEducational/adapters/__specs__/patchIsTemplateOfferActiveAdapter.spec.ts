import { api } from 'apiClient/api'
import {
  offerAdageActivated,
  offerAdageDeactivate,
} from 'core/OfferEducational/constants'

import { patchIsTemplateOfferActiveAdapter } from '../patchIsTemplateOfferActiveAdapter'

describe('patchIsTemplateOfferActiveAdapter', () => {
  const offerId = 12
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
      offerId: 0,
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
      offerId: offerId,
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
      offerId: offerId,
      isActive: false,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(offerAdageDeactivate)
  })
  it('should confirm when the offer was deactivated', async () => {
    // given
    jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockResolvedValue()

    // when
    const response = await patchIsTemplateOfferActiveAdapter({
      offerId: offerId,
      isActive: true,
    })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe(offerAdageActivated)
  })
})
