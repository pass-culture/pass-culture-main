import { api } from 'apiClient/api'
import {
  ApiError,
  CollectiveOfferFromTemplateResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { EducationalOfferType } from 'core/OfferEducational'

import { patchCollectiveOfferTemplateIntoCollectiveOfferAdapter } from '../patchCollectiveOfferTemplateIntoCollectiveOffer'

describe('patchCollectiveOfferTemplateIntoCollectiveOfferAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given / when
    const response =
      await patchCollectiveOfferTemplateIntoCollectiveOfferAdapter({
        offerId: '',
        departmentCode: '1',
        values: {
          eventDate: new Date(),
          eventTime: new Date(),
          numberOfPlaces: 1,
          priceDetail: '',
          totalPrice: 20,
          bookingLimitDatetime: null,
          educationalOfferType: EducationalOfferType.CLASSIC,
        },
      })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une erreur est survenue lors de la mise à jour de votre stock. L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should return an error when there is an error in the form', async () => {
    // given
    jest
      .spyOn(api, 'transformCollectiveOfferTemplateIntoCollectiveOffer')
      .mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          { body: {}, status: 400 } as ApiResult,
          ''
        )
      )

    // when
    const response =
      await patchCollectiveOfferTemplateIntoCollectiveOfferAdapter({
        offerId: '12',
        departmentCode: '1',
        values: {
          eventDate: new Date(),
          eventTime: new Date(),
          numberOfPlaces: 1,
          priceDetail: '',
          totalPrice: 20,
          bookingLimitDatetime: null,
          educationalOfferType: EducationalOfferType.CLASSIC,
        },
      })

    // then
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(
      'Une ou plusieurs erreurs sont présentes dans le formulaire'
    )
  })

  it('should return a confirmation when the offer was updated', async () => {
    // given
    jest
      .spyOn(api, 'transformCollectiveOfferTemplateIntoCollectiveOffer')
      .mockResolvedValue({} as CollectiveOfferFromTemplateResponseModel)

    // when
    const response =
      await patchCollectiveOfferTemplateIntoCollectiveOfferAdapter({
        offerId: '12',
        departmentCode: '1',
        values: {
          eventDate: new Date(),
          eventTime: new Date(),
          numberOfPlaces: 1,
          priceDetail: '',
          totalPrice: 20,
          bookingLimitDatetime: null,
          educationalOfferType: EducationalOfferType.CLASSIC,
        },
      })

    // then
    expect(response.isOk).toBeTruthy()
    expect(response.message).toBe('Votre stock a bien été modifiée.')
  })
})
