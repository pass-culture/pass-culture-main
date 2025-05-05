import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'

import { getIndividualOfferImage } from '../getIndividualOfferImage'

describe('getIndividualOfferImage', () => {
  const serializeOfferApiImageDataSet = [
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: 'John Do',
      },
      expectedImage: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: 'John Do',
      },
    },
    {
      activeMediation: {},
      expectedImage: undefined,
    },
    {
      activeMediation: {
        credit: 'John Do',
      },
      expectedImage: undefined,
    },
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: null,
      },
      expectedImage: {
        originalUrl: 'https://image.url',
        url: 'https://image.url',
        credit: '',
      },
    },
  ]

  it.each(serializeOfferApiImageDataSet)(
    'using image from mediation',
    ({ activeMediation, expectedImage }) => {
      const offerApi = getIndividualOfferFactory({
        activeMediation,
      })

      expect(getIndividualOfferImage(offerApi)).toEqual(expectedImage)
    }
  )

  it('using image from thumbUrl', () => {
    const offer = getIndividualOfferFactory({
      thumbUrl: 'https://image.url',
      activeMediation: undefined,
    })

    expect(getIndividualOfferImage(offer)).toEqual({
      originalUrl: 'https://image.url',
      url: 'https://image.url',
      credit: '',
    })
  })

  it('should return undefined when no image is available', () => {
    expect(getIndividualOfferImage(null)).toBeUndefined()
  })
})
