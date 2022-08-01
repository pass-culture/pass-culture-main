import { api } from 'apiClient/api'
import {
  ApiError,
  GetCollectiveOfferTemplateResponseModel,
  OfferAddressType,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import {
  Params,
  patchCollectiveOfferTemplateAdapter,
} from '../patchCollectiveOfferTemplateAdapter'

describe('patchCollectiveOfferTemplateAdapter', () => {
  let props: Params
  beforeEach(() => {
    props = {
      offerId: '12',
      offer: {
        category: 'PRATIQUE_ART',
        subCategory: SubcategoryIdEnum.ATELIER_PRATIQUE_ART,
        title: 'CollectiveOffer 0',
        description: 'A passionate description of collectiveoffer 0',
        duration: '',
        offererId: 'BU',
        venueId: 'DY',
        eventAddress: {
          addressType: OfferAddressType.OTHER,
          otherAddress: '1 rue des polissons, Paris 75017',
          venueId: '',
        },
        interventionArea: [],
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
        domains: [],
      },
      initialValues: {
        category: 'PRATIQUE_ART',
        subCategory: SubcategoryIdEnum.ATELIER_PRATIQUE_ART,
        title: 'CollectiveOffer 0',
        description: 'A passionate description of collectiveoffer 0',
        duration: '',
        offererId: 'BU',
        venueId: 'DY',
        eventAddress: {
          addressType: OfferAddressType.OTHER,
          otherAddress: '1 rue des polissons, Paris 75017',
          venueId: '',
        },
        interventionArea: [],
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
        domains: [],
      },
    }
  })

  describe('patchCollectiveOfferTemplateAdapter', () => {
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
      jest
        .spyOn(api, 'editCollectiveOfferTemplate')
        .mockRejectedValueOnce(
          new ApiError(
            {} as ApiRequestOptions,
            { body: {}, status: 422 } as ApiResult,
            ''
          )
        )

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
      jest
        .spyOn(api, 'editCollectiveOfferTemplate')
        .mockResolvedValueOnce({} as GetCollectiveOfferTemplateResponseModel)

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
