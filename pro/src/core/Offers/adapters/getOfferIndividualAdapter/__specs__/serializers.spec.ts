import {
  GetIndividualOfferResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferStockResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import {
  IOfferIndividual,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

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
      cancellationLimitDate: '01-05-2001',
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      dateModifiedAtLastProvider: null,
      fieldsUpdated: [],
      hasActivationCode: false,
      id: 'stock_id',
      idAtProviders: null,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      lastProviderId: null,
      offerId: 'offer_id',
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
      id: 'stock_id',
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      offerId: 'offer_id',
      price: 150,
      quantity: 20,
      remainingQuantity: 10,
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })
  it('serializeStockApi product', async () => {
    const stock: GetOfferStockResponseModel = {
      bookingsQuantity: 10,
      cancellationLimitDate: '01-05-2001',
      dateCreated: '01-01-1999',
      dateModified: '01-12-1999',
      dateModifiedAtLastProvider: null,
      fieldsUpdated: [],
      hasActivationCode: false,
      id: 'stock_id',
      idAtProviders: null,
      isBookable: true,
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      lastProviderId: null,
      offerId: 'offer_id',
      price: 150,
      quantity: 20,
    }

    const stockSerialized: IOfferIndividualStock = {
      beginningDatetime: null,
      bookingLimitDatetime: null,
      bookingsQuantity: 10,
      dateCreated: new Date('01-01-1999'),
      hasActivationCode: false,
      id: 'stock_id',
      isEventDeletable: false,
      isEventExpired: false,
      isSoftDeleted: false,
      offerId: 'offer_id',
      price: 150,
      quantity: 20,
      remainingQuantity: 0,
    }

    expect(serializeStockApi(stock)).toEqual(stockSerialized)
  })

  const serializeOfferApiImageDataSet = [
    {
      mediations: [
        {
          thumbUrl: 'http://image.url',
          credit: 'John Do',
          dateCreated: '01-01-2001',
          fieldsUpdated: [],
          id: 'image_id',
          isActive: true,
          offerId: 'offer_id',
          thumbCount: 1,
        },
      ] as unknown as GetIndividualOfferResponseModel[],
      expectedImage: {
        originalUrl: 'http://image.url',
        url: 'http://image.url',
        credit: 'John Do',
      },
    },
    {
      mediations: [] as unknown as GetIndividualOfferResponseModel[],
      expectedImage: undefined,
    },
    {
      mediations: [
        { credit: 'John Do' },
      ] as unknown as GetIndividualOfferResponseModel[],
      expectedImage: undefined,
    },
    {
      mediations: [
        {
          thumbUrl: 'http://image.url',
          credit: null,
          dateCreated: '01-01-2001',
          fieldsUpdated: [],
          id: 'image_id',
          isActive: true,
          offerId: 'offer_id',
          thumbCount: 1,
        },
      ] as unknown as GetIndividualOfferResponseModel[],
      expectedImage: {
        originalUrl: 'http://image.url',
        url: 'http://image.url',
        credit: '',
      },
    },
  ]
  it.each(serializeOfferApiImageDataSet)(
    'serializeOfferApiImage',
    ({ mediations, expectedImage }) => {
      const offerApi = {
        mediations,
      } as unknown as GetIndividualOfferResponseModel

      expect(serializeOfferApiImage(offerApi)).toEqual(expectedImage)
    }
  )
  it('serializeOffererApi', async () => {
    const offerApi = {
      venue: {
        managingOfferer: {
          id: 'Offerer ID',
          name: 'Offerer name',
        },
      },
    } as unknown as GetIndividualOfferResponseModel
    const offerer: IOfferIndividualOfferer = {
      id: 'Offerer ID',
      name: 'Offerer name',
    }

    expect(serializeOffererApi(offerApi)).toEqual(offerer)
  })

  it('serializeVenueApi', async () => {
    const offerApi = {
      venue: {
        id: 'venue id',
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
          name: 'Offerer name',
        },
      },
    } as unknown as GetIndividualOfferResponseModel
    const venue: IOfferIndividualVenue = {
      id: 'venue id',
      name: 'venue name',
      publicName: 'venue publicName',
      isVirtual: false,
      address: 'venue address',
      postalCode: 'venue postalCode',
      departmentCode: '75',
      city: 'venue city',
      offerer: {
        id: 'Offerer ID',
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
      enabledForPro: true,
      id: 'venueProvider ID',
      isActive: true,
      name: 'Awesom provider',
    }
    const provider: IOfferIndividualVenueProvider = {
      id: 'venueProvider ID',
      isActive: true,
      name: 'Awesom provider',
    }

    expect(serializeLastProvider(venueProviderApi)).toEqual(provider)
  })
  it('serializeOfferApi', async () => {
    const offerApi: GetIndividualOfferResponseModel = {
      activeMediation: null,
      ageMax: null,
      ageMin: null,
      bookingEmail: null,
      conditions: null,
      dateCreated: '2022-05-18T08:25:30.991476Z',
      dateModifiedAtLastProvider: '2022-05-18T08:25:30.991481Z',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      extraData: null,
      fieldsUpdated: [],
      hasBookingLimitDatetimesPassed: true,
      id: 'YA',
      isActive: true,
      isBookable: false,
      isDigital: false,
      isDuo: false,
      isEditable: true,
      isEducational: false,
      isEvent: true,
      isNational: false,
      isThing: false,
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      nonHumanizedId: 192,
      visualDisabilityCompliant: false,
      lastProvider: {
        enabledForPro: true,
        isActive: true,
        id: 'LP',
        name: 'My Last Provider',
      },
      lastProviderId: 'LP',
      mediaUrls: [],
      mediations: [
        {
          thumbUrl: 'http://my.thumb.url',
          credit: 'John Do',
          dateCreated: '01-01-2000',
          fieldsUpdated: [],
          id: 'AA',
          isActive: true,
          offerId: 'YA',
          thumbCount: 1,
        },
      ],
      name: 'Séance ciné duo',
      product: {
        ageMax: null,
        ageMin: null,
        conditions: null,
        dateModifiedAtLastProvider: '2022-05-18T08:25:30.980975Z',
        description: 'A passionate description of product 80',
        durationMinutes: null,
        extraData: null,
        fieldsUpdated: [],
        id: 'AJFA',
        idAtProviders: null,
        isGcuCompatible: true,
        isNational: false,
        lastProviderId: null,
        mediaUrls: [],
        name: 'Product 80',
        owningOffererId: null,
        thumbCount: 0,
        url: null,
      },
      productId: 'AJFA',
      stocks: [
        {
          beginningDatetime: '2022-05-23T08:25:31.009799Z',
          bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
          bookingsQuantity: 2,
          cancellationLimitDate: '2022-06-01T12:15:12.343431Z',
          dateCreated: '2022-05-18T08:25:31.015652Z',
          dateModified: '2022-05-18T08:25:31.015655Z',
          dateModifiedAtLastProvider: '2022-05-18T08:25:31.015643Z',
          fieldsUpdated: [],
          hasActivationCode: false,
          id: 'YE',
          idAtProviders: null,
          isBookable: false,
          isEventDeletable: false,
          isEventExpired: true,
          isSoftDeleted: false,
          lastProviderId: null,
          offerId: 'YA',
          price: 10,
          quantity: 1000,
          remainingQuantity: 998,
        },
      ],
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      thumbUrl: null,
      externalTicketOfficeUrl: null,
      url: null,
      venue: {
        address: '1 boulevard Poissonnière',
        bookingEmail: 'venue29@example.net',
        city: 'Paris',
        comment: null,
        dateCreated: '2022-05-18T08:25:30.929961Z',
        dateModifiedAtLastProvider: '2022-05-18T08:25:30.929955Z',
        departementCode: '75',
        fieldsUpdated: [],
        id: 'DY',
        idAtProviders: null,
        isValidated: true,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.87004,
        longitude: 2.3785,
        managingOfferer: {
          address: '1 boulevard Poissonnière',
          city: 'Paris',
          dateCreated: '2022-05-18T08:25:30.891369Z',
          dateModifiedAtLastProvider: '2022-05-18T08:25:30.891364Z',
          fieldsUpdated: [],
          id: 'CU',
          idAtProviders: null,
          isActive: true,
          isValidated: true,
          lastProviderId: null,
          name: 'Le Petit Rintintin Management 6',
          postalCode: '75000',
          siren: '000000006',
          thumbCount: 0,
        },
        managingOffererId: 'CU',
        name: 'Cinéma synchro avec booking provider',
        postalCode: '75000',
        publicName: 'Cinéma synchro avec booking provider',
        siret: '00000000600029',
        thumbCount: 0,
        venueLabelId: null,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
      },
      venueId: 'DY',
      withdrawalDetails: null,
      status: OfferStatus.EXPIRED,
      withdrawalType: null,
      withdrawalDelay: null,
    }
    const offerSerialized: IOfferIndividual = {
      id: 'YA',
      author: '',
      bookingEmail: '',
      description: 'A passionate description of product 80',
      durationMinutes: null,
      isbn: '',
      isDuo: false,
      isEducational: false,
      accessibility: {
        none: true,
        audio: false,
        mental: false,
        motor: false,
        visual: false,
      },
      isNational: false,
      name: 'Séance ciné duo',
      isEvent: true,
      withdrawalType: null,
      image: {
        originalUrl: 'http://my.thumb.url',
        url: 'http://my.thumb.url',
        credit: 'John Do',
      },
      musicSubType: '',
      musicType: '',
      nonHumanizedId: 192,
      offererId: 'CU',
      offererName: 'Le Petit Rintintin Management 6',
      performer: '',
      showSubType: '',
      showType: '',
      stageDirector: '',
      speaker: '',
      status: OfferStatus.EXPIRED,
      subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
      url: '',
      externalTicketOfficeUrl: '',
      venueId: 'DY',
      visa: '',
      withdrawalDetails: '',
      withdrawalDelay: null,
      lastProvider: {
        isActive: true,
        id: 'LP',
        name: 'My Last Provider',
      },
      lastProviderName: 'My Last Provider',
      stocks: [
        {
          beginningDatetime: '2022-05-23T08:25:31.009799Z',
          bookingLimitDatetime: '2022-05-23T07:25:31.009799Z',
          bookingsQuantity: 2,
          dateCreated: new Date('2022-05-18T08:25:31.015652Z'),
          hasActivationCode: false,
          id: 'YE',
          isEventDeletable: false,
          isEventExpired: true,
          isSoftDeleted: false,
          offerId: 'YA',
          price: 10,
          quantity: 1000,
          remainingQuantity: 998,
        },
      ],
      venue: {
        address: '1 boulevard Poissonnière',
        city: 'Paris',
        id: 'DY',
        isVirtual: false,
        name: 'Cinéma synchro avec booking provider',
        offerer: {
          id: 'CU',
          name: 'Le Petit Rintintin Management 6',
        },
        postalCode: '75000',
        publicName: 'Cinéma synchro avec booking provider',
        departmentCode: '75',
        accessibility: {
          none: true,
          audio: false,
          mental: false,
          motor: false,
          visual: false,
        },
      },
    }

    expect(serializeOfferApi(offerApi)).toEqual(offerSerialized)
  })
})
