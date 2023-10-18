import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import {
  IndividualOffer,
  IndividualOfferStock,
  IndividualOfferVenue,
  IndividualOfferVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { GetIndividualOfferFactory } from 'utils/apiFactories'

import {
  serializeStockApi,
  serializeOfferApiImage,
  serializeVenueApi,
  serializeOfferApiExtraData,
  serializeLastProvider,
  serializeOfferApi,
} from '../serializers'

describe('serializer', () => {
  it('serializeStockApi', () => {
    const stock: GetOfferStockResponseModel = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      id: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
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
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      id: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: '01-01-2001',
      bookingLimitDatetime: '01-10-2001',
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
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
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      hasActivationCode: false,
      id: 1,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      price: 150,
      quantity: 20,
    }

    const stockSerialized: IndividualOfferStock = {
      beginningDatetime: null,
      bookingLimitDatetime: null,
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
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

  it('serializeVenueApi', () => {
    const venueId = 1
    const offerApi = {
      venue: {
        id: venueId,
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
          id: 1,
          name: 'Offerer name',
        },
      },
    } as unknown as GetIndividualOfferResponseModel
    const venue: IndividualOfferVenue = {
      id: venueId,
      name: 'venue name',
      publicName: 'venue publicName',
      isVirtual: false,
      address: 'venue address',
      postalCode: 'venue postalCode',
      departmentCode: '75',
      city: 'venue city',
      offerer: {
        id: 1,
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

  it('serializeLastProvider with empty input', () => {
    expect(serializeLastProvider(null)).toEqual(null)
  })

  it('serializeLastProvider', () => {
    const venueProviderApi: GetOfferLastProviderResponseModel = {
      name: 'Awesom provider',
    }
    const provider: IndividualOfferVenueProvider = {
      name: 'Awesom provider',
    }

    expect(serializeLastProvider(venueProviderApi)).toEqual(provider)
  })

  it('serializeOfferApi', () => {
    const offerApi: GetIndividualOfferResponseModel =
      GetIndividualOfferFactory()
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
      description: '',
      durationMinutes: null,
      ean: '',
      externalTicketOfficeUrl: '',
      image: undefined,
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
          id: 1,
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
