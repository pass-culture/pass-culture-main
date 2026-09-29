import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

describe('getIndividualOfferImage', () => {
  const serializeOfferApiImageDataSet = [
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: 'John Do',
        alternativeText: 'an alt text',
        authorId: null,
      },
      expectedImage: {
        url: 'https://image.url',
        credit: 'John Do',
        alternativeText: 'an alt text',
      },
    },
    {
      activeMediation: null,
      expectedImage: undefined,
    },
    {
      activeMediation: {
        thumbUrl: null,
        credit: 'John Do',
        alternativeText: null,
        authorId: null,
      },
      expectedImage: undefined,
    },
    {
      activeMediation: {
        thumbUrl: 'https://image.url',
        credit: null,
        alternativeText: null,
        authorId: null,
      },
      expectedImage: {
        url: 'https://image.url',
        credit: '',
        alternativeText: '',
      },
    },
  ]

  it.each(serializeOfferApiImageDataSet)(
    'using image from mediation %s',
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
      alternativeText: '',
    })
  })

  it('should return undefined when no image is available', () => {
    expect(getIndividualOfferImage(null)).toBeUndefined()
  })
})
