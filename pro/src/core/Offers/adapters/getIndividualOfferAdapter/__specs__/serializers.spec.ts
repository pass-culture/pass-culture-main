import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { IndividualOffer, IndividualOfferStock } from 'core/Offers/types'
import { GetIndividualOfferFactory } from 'utils/apiFactories'

import {
  serializeStockApi,
  serializeOfferApiImage,
  serializeOfferApiExtraData,
  serializeOfferApi,
} from '../serializers'

describe('serializer', () => {
  it('serializeStockApi', () => {
    const stock: GetOfferStockResponseModel = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      hasActivationCode: false,
      id: 1,
      isEventDeletable: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      hasActivationCode: false,
      isEventDeletable: false,
      id: 1,
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
      activationCodesExpirationDatetime: null,
      activationCodes: [],
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })

  it('serializeStockApi with 0 remainingQuantity', () => {
    const stock: GetOfferStockResponseModel = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      hasActivationCode: false,
      id: 1,
      isEventDeletable: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      hasActivationCode: false,
      isEventDeletable: false,
      id: 1,
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
      activationCodesExpirationDatetime: null,
      activationCodes: [],
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })

  it('serializeStockApi product', () => {
    const stock: GetOfferStockResponseModel = {
      bookingsQuantity: 10,
      hasActivationCode: false,
      id: 1,
      isEventDeletable: false,
      price: 150,
      quantity: 20,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: null,
      bookingLimitDatetime: null,
      bookingsQuantity: 10,
      hasActivationCode: false,
      isEventDeletable: false,
      id: 1,
      price: 150,
      quantity: 20,
      remainingQuantity: 'unlimited',
      activationCodesExpirationDatetime: null,
      activationCodes: [],
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })

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
    const offerSerialized: IndividualOffer = {
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
      description: '',
      durationMinutes: null,
      ean: '',
      externalTicketOfficeUrl: '',
      image: undefined,
      hasStocks: true,
      isActive: true,
      isActivable: true,
      isDigital: false,
      isDuo: true,
      isEvent: false,
      isNational: true,
      lastProvider: null,
      lastProviderName: null,
      musicSubType: '',
      musicType: '',
      name: 'Le nom de l’offre 1',
      id: 1,
      offererId: offerApi.venue.managingOfferer.id,
      offererName: 'Le nom de la structure 1',
      performer: '',
      priceCategories: undefined,
      showSubType: '',
      showType: '',
      speaker: '',
      stageDirector: '',
      status: OfferStatus.ACTIVE,
      stocks: [
        {
          activationCodes: [],
          activationCodesExpirationDatetime: null,
          beginningDatetime: '2021-10-15T12:00:00.000Z',
          bookingLimitDatetime: '2021-09-15T12:00:00.000Z',
          bookingsQuantity: 0,
          hasActivationCode: false,
          id: 1,
          isEventDeletable: true,
          price: 10,
          quantity: 18,
          remainingQuantity: 'unlimited',
          priceCategoryId: 2,
        },
      ],
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
      venueId: 1,
      visa: '',
      withdrawalDelay: null,
      withdrawalDetails: '',
      withdrawalType: null,
    }

    expect(serializeOfferApi(offerApi)).toEqual(offerSerialized)
  })
})
