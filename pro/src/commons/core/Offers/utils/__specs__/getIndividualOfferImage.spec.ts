import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

describe('getIndividualOfferImage', () => {
  const serializeOfferApiImageDataSet = [
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: 'John Do',
      },
      expectedImage: {
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
      url: 'https://image.url',
      credit: '',
    })
  })

  it('should return undefined when no image is available', () => {
    expect(getIndividualOfferImage(null)).toBeUndefined()
  })
})
