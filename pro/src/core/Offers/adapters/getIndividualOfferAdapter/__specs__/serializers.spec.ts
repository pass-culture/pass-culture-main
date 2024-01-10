import { GetIndividualOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { GetIndividualOfferFactory } from 'utils/apiFactories'

import {
  serializeOfferApiImage,
  serializeOfferApiExtraData,
  serializeOfferApi,
} from '../serializers'

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

  it('serializeOfferApiExtraData', () => {
    const offerApi = {
      extraData: {
        author: 'test author',
        musicType: 'test musicType',
        musicSubType: 'test musicSubType',
        performer: 'test performer',
        ean: 'test ean',
        showType: 'test showType',
        showSubType: 'test showSubType',
        speaker: 'test speaker',
        stageDirector: 'test stageDirector',
        visa: 'test visa',
      },
    } as unknown as GetIndividualOfferResponseModel

    expect(serializeOfferApiExtraData(offerApi)).toEqual({
      author: 'test author',
      musicType: 'test musicType',
      musicSubType: 'test musicSubType',
      performer: 'test performer',
      ean: 'test ean',
      showType: 'test showType',
      showSubType: 'test showSubType',
      speaker: 'test speaker',
      stageDirector: 'test stageDirector',
      visa: 'test visa',
    })
  })

  it('serializeOfferApi', () => {
    const offerApi: GetIndividualOfferResponseModel = GetIndividualOfferFactory(
      { bookingsCount: 123 }
    )
    const offerSerialized = {
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        none: true,
        visual: false,
      },
      author: '',
      bookingEmail: '',
      bookingContact: '',
      bookingsCount: 123,
      dateCreated: '2020-04-12T19:31:12Z',
      description: '',
      durationMinutes: null,
      ean: '',
      externalTicketOfficeUrl: '',
      image: undefined,
      hasBookingLimitDatetimesPassed: false,
      hasStocks: true,
      isActive: true,
      isActivable: true,
      isDigital: false,
      isDuo: true,
      isEditable: true,
      isEvent: false,
      isNational: true,
      isNonFreeOffer: true,
      isThing: true,
      lastProvider: null,
      lastProviderName: null,
      musicSubType: '',
      musicType: '',
      name: 'Le nom de l’offre 1',
      id: 1,
      performer: '',
      priceCategories: undefined,
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      status: OfferStatus.ACTIVE,
      subcategoryId: 'SEANCE_CINE',
      url: '',
      venue: {
        id: 1,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        address: 'Ma Rue',
        city: 'Ma Ville',
        departementCode: '78',
        isVirtual: false,
        name: 'Le nom du lieu 1',
        managingOfferer: {
          name: 'Le nom de la structure 1',
          id: 3,
        },
        postalCode: '11100',
        publicName: 'Mon Lieu',
      },
      visa: '',
      withdrawalDelay: null,
      withdrawalDetails: '',
      withdrawalType: null,
    }

    expect(serializeOfferApi(offerApi)).toEqual(offerSerialized)
  })
})
