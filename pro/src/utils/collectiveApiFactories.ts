/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import {
  CategoryResponseModel,
  CollectiveBookingBankInformationStatus,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
  DMSApplicationForEAC,
  DMSApplicationstatus,
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
  GetCollectiveOfferCollectiveStockResponseModel,
  GetCollectiveOfferManagingOffererResponseModel,
  GetCollectiveOfferVenueResponseModel,
  GetCollectiveVenueResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { BOOKING_STATUS } from 'core/Bookings'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import { IVenue } from 'core/Venue'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let bookingId = 1
let bookingDetailsId = 1
let categoryId = 1
let subCategoryId = 1
let institutionId = 1

const sharedCollectiveOfferData = {
  isActive: true,
  status: OfferStatus.ACTIVE,
  isCancellable: true,
  isTemplate: true,
  name: 'Offre de test',
  bookingEmails: ['toto@example.com'],
  contactEmail: 'toto@example.com',
  contactPhone: '0600000000',
  dateCreated: new Date().toISOString(),
  description: 'blablabla,',
  domains: [{ id: 1, name: 'Danse' }],
  hasBookingLimitDatetimesPassed: false,
  interventionArea: ['mainland'],
  isEditable: true,
  isPublicApi: false,
  nonHumanizedId: 123,
  offerVenue: {
    venueId: null,
    otherAddress: 'A la mairie',
    addressType: OfferAddressType.OTHER,
  },
  students: [StudentLevels.COLL_GE_3E],
  subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
  venueId: 'VENUE_ID',
  imageUrl: 'https://example.com/image.jpg',
  imageCredit: 'image credit',
}

export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<CollectiveOffer> = {},
  customStock: GetCollectiveOfferCollectiveStockResponseModel = collectiveStockFactory() ||
    null,
  customVenue: GetCollectiveOfferVenueResponseModel = collectiveOfferVenueFactory()
): CollectiveOffer => {
  const stock = customStock === null ? null : customStock
  const currentOfferId = offerId++
  return {
    ...sharedCollectiveOfferData,
    id: currentOfferId.toString(),
    nonHumanizedId: currentOfferId,
    venue: customVenue,
    isBookable: true,
    isVisibilityEditable: true,
    isTemplate: false,
    collectiveStock: stock,
    ...customCollectiveOffer,
  }
}

export const collectiveStockFactory = (
  customStock: Partial<GetCollectiveOfferCollectiveStockResponseModel> = {}
): GetCollectiveOfferCollectiveStockResponseModel => {
  const currentStockId = stockId++
  return {
    id: `STOCK${currentStockId}`,
    nonHumanizedId: currentStockId,
    price: 100,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    isBooked: false,
    isCancellable: false,
    isEducationalStockEditable: true,
    ...customStock,
  }
}

export const collectiveOfferTemplateFactory = (
  customCollectiveOfferTemplate: Partial<CollectiveOfferTemplate> = {},
  customVenue: GetCollectiveOfferVenueResponseModel = collectiveOfferVenueFactory()
): CollectiveOfferTemplate => ({
  ...sharedCollectiveOfferData,
  id: (offerId++).toString(),
  venue: customVenue,
  isTemplate: true,
  ...customCollectiveOfferTemplate,
})

export const collectiveOfferVenueFactory = (
  customVenue: Partial<GetCollectiveOfferVenueResponseModel> = {},
  customOfferer: GetCollectiveOfferManagingOffererResponseModel = collectiveOfferOffererFactory()
): GetCollectiveOfferVenueResponseModel => {
  const currentVenueId = venueId++
  return {
    address: 'Ma Rue',
    city: 'Ma Ville',
    id: `VENUE${currentVenueId}`,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: customOfferer,
    managingOffererId: customOfferer.id,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    nonHumanizedId: currentVenueId,
    departementCode: '973',
    fieldsUpdated: [],
    thumbCount: 0,
    ...customVenue,
  }
}

export const collectiveOfferOffererFactory = (
  customOfferer: Partial<GetCollectiveOfferManagingOffererResponseModel> = {}
): GetCollectiveOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    id: `OFFERER${currentOffererId}`,
    nonHumanizedId: currentOffererId,
    name: `La nom de la structure ${currentOffererId}`,
    city: 'Paris',
    dateCreated: new Date().toISOString(),
    isActive: true,
    isValidated: true,
    postalCode: '75018',
    thumbCount: 0,
    ...customOfferer,
  }
}

export const collectiveBookingRecapFactory = (
  customBookingRecap: Partial<CollectiveBookingResponseModel> = {}
): CollectiveBookingResponseModel => {
  const currentBookingId = bookingId++
  return {
    bookingAmount: 1,
    bookingCancellationLimitDate: new Date().toISOString(),
    bookingConfirmationDate: new Date().toISOString(),
    bookingConfirmationLimitDate: new Date().toISOString(),
    bookingDate: new Date().toISOString(),
    bookingId: currentBookingId.toString(),
    bookingIdentifier: currentBookingId.toString(),
    bookingIsDuo: false,
    bookingStatus: BOOKING_STATUS.PENDING,
    bookingStatusHistory: [
      { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
    ],
    bookingToken: null,
    institution: {
      city: 'PARIS',
      id: 1,
      institutionId: '1',
      institutionType: null,
      name: 'COLLEGE DE PARIS',
      postalCode: '75001',
      phoneNumber: '0601020304',
    },
    stock: {
      bookingLimitDatetime: new Date().toISOString(),
      eventBeginningDatetime: new Date().toISOString(),
      numberOfTickets: 1,
      offerIdentifier: '1',
      offerIsEducational: true,
      offerIsbn: null,
      offerName: 'ma super offre collective',
    },
    ...customBookingRecap,
  }
}
export const defaultCollectiveBookingStock = {
  bookingLimitDatetime: new Date().toISOString(),
  eventBeginningDatetime: new Date().toISOString(),
  numberOfTickets: 1,
  offerIdentifier: '1',
  offerIsEducational: true,
  offerIsbn: null,
  offerName: 'ma super offre collective',
}

export const collectiveBookingDetailsFactory = (
  customBookingDetails?: Partial<CollectiveBookingByIdResponseModel>
): CollectiveBookingByIdResponseModel => {
  const currentBookingDetailsId = bookingDetailsId++
  return {
    bankInformationStatus: CollectiveBookingBankInformationStatus.ACCEPTED,
    beginningDatetime: new Date().toISOString(),
    educationalInstitution: {
      city: 'Paris',
      id: 1,
      institutionId: '1',
      institutionType: 'LYCEE',
      name: 'De Paris',
      phoneNumber: '0601020304',
      postalCode: '75000',
    },
    educationalRedactor: {
      civility: 'Mr',
      email: 'test@example.com',
      firstName: 'Jean',
      id: 1,
      lastName: 'Dupont',
    },
    id: currentBookingDetailsId,
    isCancellable: true,
    numberOfTickets: 1,
    offerVenue: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: '',
      venueId: 1,
    },
    offererId: 'O1',
    price: 100,
    students: [StudentLevels.LYC_E_SECONDE],
    venueDMSApplicationId: 1,
    venueId: 'V1',
    venuePostalCode: '75000',
    ...customBookingDetails,
  }
}

export const venueCollectiveDataFactory = (
  customCollectiveData: Partial<GetCollectiveVenueResponseModel> = {}
): GetCollectiveVenueResponseModel => {
  return {
    id: 'A1',
    collectiveDomains: [],
    collectiveDescription: '',
    collectiveEmail: '',
    collectiveInterventionArea: [],
    collectiveLegalStatus: null,
    collectiveNetwork: [],
    collectivePhone: '',
    collectiveStudents: [],
    collectiveWebsite: '',
    collectiveSubCategoryId: '',
    siret: '1234567890',
    ...customCollectiveData,
  }
}

export const collectiveCategoryFactory = (
  customCategory?: Partial<CategoryResponseModel>
) => {
  const currentCategoryId = categoryId++
  return {
    id: `CATEGORY_${currentCategoryId}`,
    isSelectable: true,
    proLabel: `Cat numéro ${currentCategoryId}`,
    ...customCategory,
  }
}

export const collectiveSubCategoryFactory = (
  customSubCategory?: Partial<SubcategoryResponseModel>
): SubcategoryResponseModel => {
  const currentSubCategoryId = subCategoryId++
  return {
    appLabel: '',
    canBeDuo: true,
    canBeEducational: true,
    canExpire: true,
    categoryId: `CATEGORY_${currentSubCategoryId}`,
    conditionalFields: [],
    id: `SUB_CATEGORY_${currentSubCategoryId}`,
    isDigitalDeposit: false,
    isEvent: true,
    isPhysicalDeposit: false,
    isSelectable: true,
    onlineOfflinePlatform: '',
    canBeWithdrawable: false,
    proLabel: `Sous catégorie #${currentSubCategoryId}`,
    reimbursementRule: '',
    ...customSubCategory,
  }
}

export const defaultEducationalInstitution: EducationalInstitutionResponseModel =
  {
    city: 'Paris',
    id: institutionId++,
    institutionId: 'ABC123',
    institutionType: 'LYCEE',
    name: 'Sacré coeur',
    phoneNumber: '0601020304',
    postalCode: '75000',
  }

export const defaultEducationalRedactor: EducationalRedactorResponseModel = {
  civility: 'Mr',
  email: 'Jean.Dupont@example.com',
  firstName: 'Jean',
  lastName: 'Dupont',
}

export const defaultCollectiveDmsApplication: DMSApplicationForEAC = {
  application: 123,
  depositDate: new Date().toISOString(),
  lastChangeDate: new Date().toISOString(),
  procedure: 456,
  state: DMSApplicationstatus.EN_CONSTRUCTION,
  venueId: 1,
}

// FIXME : to remove while this type should be used in the future
export const defaultIVenue: IVenue = {
  id: 'V1',
  name: 'Lieu de test',
  address: '1 rue de test',
  city: 'Paris',
  postalCode: '75000',
  latitude: 48.856614,
  longitude: 2.3522219,
  collectiveDomains: [],
  dateCreated: '',
  fieldsUpdated: [],
  isVirtual: false,
  managingOffererId: '',
  accessibility: {
    none: false,
    visual: false,
    audio: false,
    motor: false,
    mental: false,
  },
  bannerMeta: undefined,
  bannerUrl: '',
  hasPendingBankInformationApplication: null,
  demarchesSimplifieesApplicationId: null,
  comment: '',
  contact: {
    email: null,
    phoneNumber: null,
    webSite: null,
  },
  description: '',
  departmentCode: '',
  dmsToken: '',
  isPermanent: false,
  isVenueVirtual: false,
  mail: '',
  managingOfferer: {
    address: undefined,
    city: '',
    dateCreated: '',
    dateModifiedAtLastProvider: undefined,
    demarchesSimplifieesApplicationId: undefined,
    fieldsUpdated: [],
    id: '',
    nonHumanizedId: 0,
    idAtProviders: undefined,
    isValidated: false,
    lastProviderId: undefined,
    name: '',
    postalCode: '',
    siren: undefined,
  },
  nonHumanizedId: 0,
  pricingPoint: null,
  publicName: '',
  siret: '',
  venueType: '',
  venueLabel: null,
  reimbursementPointId: null,
  withdrawalDetails: '',
  collectiveAccessInformation: '',
  collectiveDescription: '',
  collectiveEmail: '',
  collectiveInterventionArea: [],
  collectiveLegalStatus: null,
  collectiveNetwork: [],
  collectivePhone: '',
  collectiveStudents: [],
  collectiveWebsite: '',
  adageInscriptionDate: null,
  hasAdageId: false,
  collectiveDmsApplication: null,
}
