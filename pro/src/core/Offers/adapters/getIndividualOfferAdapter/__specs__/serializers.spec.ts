import { GetIndividualOfferResponseModel } from 'apiClient/v1'

import { serializeOfferApiImage } from '../serializers'

describe('serializer', () => {
  const serializeOfferApiImageDataSet = [
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: 'John Do',
      } as unknown as GetIndividualOfferResponseModel[],
      expectedImage: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: 'John Do',
      },
    },
    {
      activeMediation: {} as unknown as GetIndividualOfferResponseModel[],
      expectedImage: undefined,
    },
    {
      activeMediation: {
        credit: 'John Do',
      } as unknown as GetIndividualOfferResponseModel[],
      expectedImage: undefined,
    },
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: null,
      } as unknown as GetIndividualOfferResponseModel[],
      expectedImage: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: '',
      },
    },
  ]
  it.each(serializeOfferApiImageDataSet)(
    'serializeOfferApiImage from mediation',
    ({ activeMediation, expectedImage }) => {
      const offerApi = {
        activeMediation,
      } as unknown as GetIndividualOfferResponseModel

      expect(serializeOfferApiImage(offerApi)).toEqual(expectedImage)
    }
  )

  it('serializeOfferApiImage from thumbUrl', () => {
    const offerApi = {
      thumbUrl: 'https://image.url',
      mediations: [],
    } as unknown as GetIndividualOfferResponseModel

    expect(serializeOfferApiImage(offerApi)).toEqual({
      originalUrl: 'https://image.url',
      url: 'https://image.url',
      credit: '',
    })
  })
})
