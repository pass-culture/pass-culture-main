import { ApiError, OfferStatus } from 'apiClient/v1'

import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { EducationalOfferType } from 'core/OfferEducational'
import { api } from 'apiClient/api'
import { patchCollectiveOfferTemplateAdapter } from '../patchCollectiveOfferTemplateAdapter'

describe('patchCollectiveOfferTemplateAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
    const response = await patchCollectiveOfferTemplateAdapter({
      offer: {
        id: '',
        isActive: true,
        isEducational: true,
        isBooked: false,
        status: OfferStatus.PENDING,
        venueDepartmentCode: '1',
        managingOffererId: 'A1',
        isShowcase: false,
      },
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
    // @ts-ignore
    jest
      .spyOn(api, 'editCollectiveOfferTemplate')
      .mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          { body: {}, status: 400 } as ApiResult,
          ''
        )
      )

    // when
    const response = await patchCollectiveOfferTemplateAdapter({
      offer: {
        id: '12',
        isActive: true,
        isEducational: true,
        isBooked: false,
        status: OfferStatus.PENDING,
        venueDepartmentCode: '1',
        managingOffererId: 'A1',
        isShowcase: false,
      },
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
      .spyOn(window, 'fetch')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

    // when
    const response = await patchCollectiveOfferTemplateAdapter({
      offer: {
        id: '12',
        isActive: true,
        isEducational: true,
        isBooked: false,
        status: OfferStatus.PENDING,
        venueDepartmentCode: '1',
        managingOffererId: 'A1',
        isShowcase: false,
      },
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
