import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { GetIndividualOfferFactory } from 'utils/apiFactories'

import {
  serializeStockApi,
  serializeOfferApiImage,
  serializeOffererApi,
  serializeVenueApi,
  serializeOfferApiExtraData,
  serializeLastProvider,
  serializeOfferApi,
} from '../serializers'

describe('serializer', () => {
  it('serializeStockApi', async () => {
    const stock: GetOfferStockResponseModel = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      nonHumanizedId: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
    }

    const stockSerialized: IOfferIndividualStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      nonHumanizedId: 1,
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
      activationCodesExpirationDatetime: null,
      activationCodes: [],
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })
  it('serializeStockApi with 0 remainingQuantity', async () => {
    const stock: GetOfferStockResponseModel = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      nonHumanizedId: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
    }

    const stockSerialized: IOfferIndividualStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      nonHumanizedId: 1,
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
      activationCodesExpirationDatetime: null,
      activationCodes: [],
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })

  it('serializeStockApi product', async () => {
    const stock: GetOfferStockResponseModel = {
      bookingsQuantity: 10,
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      nonHumanizedId: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
    }

    const stockSerialized: IOfferIndividualStock = {
      beginningDatetime: null,
      bookingLimitDatetime: null,
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      nonHumanizedId: 1,
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
  it('serializeOffererApi', async () => {
    const offerApi = {
      venue: {
        managingOfferer: {
          id: 'Offerer ID',
          nonHumanizedId: 1,
          name: 'Offerer name',
        },
      },
    } as unknown as GetIndividualOfferResponseModel
    const offerer: IOfferIndividualOfferer = {
      nonHumanizedId: 1,
      name: 'Offerer name',
    }

    expect(serializeOffererApi(offerApi)).toEqual(offerer)
  })

  it('serializeVenueApi', async () => {
    const venueId = 1
    const offerApi = {
      venue: {
        id: 'venue id',
        nonHumanizedId: venueId,
        name: 'venue name',
        publicName: 'venue publicName',
        isVirtual: false,
        address: 'venue address',
        postalCode: 'venue postalCode',
        departementCode: '75',
        city: 'venue city',
        offerer: 'venue offerer',
        visualDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        audioDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        managingOfferer: {
          id: 'Offerer ID',
          nonHumanizedId: 1,
          name: 'Offerer name',
        },
      },
    } as unknown as GetIndividualOfferResponseModel
    const venue: IOfferIndividualVenue = {
      id: venueId,
      name: 'venue name',
      publicName: 'venue publicName',
      isVirtual: false,
      address: 'venue address',
      postalCode: 'venue postalCode',
      departmentCode: '75',
      city: 'venue city',
      offerer: {
        nonHumanizedId: 1,
        name: 'Offerer name',
      },
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
    }

    expect(serializeVenueApi(offerApi)).toEqual(venue)
  })
  it('serializeOfferApiExtraData', async () => {
    const offerApi = {
      extraData: {
        author: 'test author',
        isbn: 'test isbn',
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
      isbn: 'test isbn',
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
  it('serializeLastProvider with empty input', async () => {
    expect(serializeLastProvider(null)).toEqual(null)
  })
  it('serializeLastProvider', async () => {
    const venueProviderApi: GetOfferLastProviderResponseModel = {
      name: 'Awesom provider',
    }
    const provider: IOfferIndividualVenueProvider = {
      name: 'Awesom provider',
    }

    expect(serializeLastProvider(venueProviderApi)).toEqual(provider)
  })
  it('serializeOfferApi', async () => {
    const offerApi: GetIndividualOfferResponseModel =
      GetIndividualOfferFactory()
    const offerSerialized: IOfferIndividual = {
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        none: true,
        visual: false,
      },
      author: '',
      bookingEmail: '',
      description: '',
      durationMinutes: null,
      ean: '',
      externalTicketOfficeUrl: '',
      image: undefined,
      isActive: true,
      isDigital: false,
      isDuo: true,
      isEvent: false,
      isNational: true,
      isbn: '',
      lastProvider: null,
      lastProviderName: null,
      musicSubType: '',
      musicType: '',
      name: 'Le nom de l’offre 1',
      nonHumanizedId: 1,
      offererId: offerApi.venue.managingOfferer.nonHumanizedId,
      offererName: 'La nom de la structure 1',
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
          beginningDatetime: null,
          bookingLimitDatetime: null,
          bookingsQuantity: 0,
          dateCreated: new Date('2020-04-12T19:31:12.000Z'),
          hasActivationCode: false,
          nonHumanizedId: 1,
          isEventDeletable: true,
          isEventExpired: false,
          isSoftDeleted: false,
          price: 10,
          quantity: null,
          remainingQuantity: 2,
        },
      ],
      subcategoryId: 'SEANCE_CINE',
      url: '',
      venue: {
        id: 1,
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
        address: 'Ma Rue',
        city: 'Ma Ville',
        departmentCode: '973',
        isVirtual: false,
        name: 'Le nom du lieu 1',
        offerer: {
          name: 'La nom de la structure 1',
          nonHumanizedId: 3,
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
