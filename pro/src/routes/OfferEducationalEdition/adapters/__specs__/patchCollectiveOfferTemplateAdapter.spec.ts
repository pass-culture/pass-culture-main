import { OfferAddressType } from 'api/v1/gen/api'

import {
  Params,
  patchCollectiveOfferTemplateAdapter,
} from '../patchCollectiveOfferTemplateAdapter'

describe('cancelCollectiveBookingAdapter', () => {
  let props: Params
  beforeEach(() => {
    props = {
      offerId: '12',
      offer: {
        category: 'PRATIQUE_ART',
        subCategory: 'ATELIER_PRATIQUE_ART',
        title: 'CollectiveOffer 0',
        description: 'A passionate description of collectiveoffer 0',
        duration: '',
        offererId: 'BU',
        venueId: 'DY',
        eventAddress: {
          addressType: OfferAddressType.Other,
          otherAddress: '1 rue des polissons, Paris 75017',
          venueId: '',
        },
        participants: {
          quatrieme: false,
          troisieme: false,
          CAPAnnee1: false,
          CAPAnnee2: false,
          seconde: true,
          premiere: true,
          terminale: false,
        },
        accessibility: {
          audio: false,
          mental: true,
          motor: false,
          visual: false,
          none: false,
        },
        phone: '+33199006328',
        email: 'collectiveofferfactory+contact@example.com',
        notifications: true,
        notificationEmail: 'collectiveofferfactory+booking@example.com',
      },
      initialValues: {
        category: 'PRATIQUE_ART',
        subCategory: 'ATELIER_PRATIQUE_ART',
        title: 'CollectiveOffer 0',
        description: 'A passionate description of collectiveoffer 0',
        duration: '',
        offererId: 'BU',
        venueId: 'DY',
        eventAddress: {
          addressType: OfferAddressType.Other,
          otherAddress: '1 rue des polissons, Paris 75017',
          venueId: '',
        },
        participants: {
          quatrieme: false,
          troisieme: false,
          CAPAnnee1: false,
          CAPAnnee2: false,
          seconde: true,
          premiere: false,
          terminale: false,
        },
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          visual: false,
          none: true,
        },
        phone: '+33199006328',
        email: 'collectiveofferfactory+contact@example.com',
        notifications: true,
        notificationEmail: 'collectiveofferfactory+booking@example.com',
      },
    }
  })

  describe('cancelCollectiveBookingAdapter', () => {
    it('should return an error when the offer id is not valid', async () => {
      // given

      // when
      const response = await patchCollectiveOfferTemplateAdapter({
        ...props,
        offerId: '',
      })

      // then
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Une erreur est survenue lors de la modification de votre offre. L’identifiant de l’offre n’est pas valide.'
      )
    })

    it('should return an error when the offer could not be updated', async () => {
      // given
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        status: 422,
        json: async () => ({}),
      })

      // when
      const response = await patchCollectiveOfferTemplateAdapter({
        ...props,
        offerId: '12',
      })

      // then
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'Une erreur est survenue lors de la modification de votre offre.'
      )
    })
    it('should return a confirmation when the booking was cancelled', async () => {
      // given
      // @ts-ignore
      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ collectiveStock: { isBooked: false } }),
      })

      // when
      const response = await patchCollectiveOfferTemplateAdapter({
        ...props,
        offerId: '12',
      })
      // then
      expect(response.isOk).toBeTruthy()
      expect(response.message).toBe('Votre offre a bien été modifiée.')
    })
  })
})
