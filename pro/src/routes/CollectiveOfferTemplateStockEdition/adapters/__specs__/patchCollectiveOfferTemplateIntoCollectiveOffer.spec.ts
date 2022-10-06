import { EducationalOfferType } from 'core/OfferEducational'

import { patchCollectiveOfferTemplateIntoCollectiveOfferAdapter } from '../patchCollectiveOfferTemplateIntoCollectiveOffer'

describe('patchCollectiveOfferTemplateIntoCollectiveOfferAdapter', () => {
  it('should return an error when the offer id is not valid', async () => {
    // given

    // when
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
    // @ts-ignore
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      status: 400,
      json: async () => ({
        code: '',
      }),
    })

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
      .spyOn(window, 'fetch')
      .mockResolvedValueOnce(new Response(new Blob(), { status: 204 }))

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
