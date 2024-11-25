/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import { OpenAPIConfig } from 'apiClient/core/OpenAPI'
import { request } from 'apiClient/customRequest'
import { ApiRequestOptions } from 'apiClient/core/ApiRequestOptions'
import { CancelablePromise } from 'apiClient/core/CancelablePromise'

/**
 *
 * @export
 */
export const COLLECTION_FORMATS = {
  csv: ',',
  ssv: ' ',
  tsv: '\t',
  pipes: '|',
}

/**
 *
 * @export
 * @class BaseAPI
 */
export class BaseAPI {
  protected configuration: OpenAPIConfig

  constructor(configuration: OpenAPIConfig) {
    this.configuration = configuration
  }
}

/**
 *
 * @export
 * @class RequiredError
 * @extends {Error}
 */
export class RequiredError extends Error {
  name = 'RequiredError'
  constructor(public field: string, msg?: string) {
    super(msg)
  }
}

/**
 * 
 * @export
 * @interface AdageCulturalPartnersResponseModel
 */
export interface AdageCulturalPartnersResponseModel {
  /**
   * 
   * @type {Array<CulturalPartner>}
   * @memberof AdageCulturalPartnersResponseModel
   */
  partners: Array<CulturalPartner>
}
/**
 * 
 * @export
 * @interface Address
 */
export interface Address {
  /**
   * 
   * @type {string}
   * @memberof Address
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof Address
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof Address
   */
  street: string
}
/**
 * 
 * @export
 * @interface AddressBodyModel
 */
export interface AddressBodyModel {
  /**
   * 
   * @type {string}
   * @memberof AddressBodyModel
   */
  city: string
  /**
   * 
   * @type {boolean}
   * @memberof AddressBodyModel
   */
  isManualEdition?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof AddressBodyModel
   */
  isVenueAddress?: boolean
  /**
   * 
   * @type {string}
   * @memberof AddressBodyModel
   */
  label?: string
  /**
   * 
   * @type {number | string}
   * @memberof AddressBodyModel
   */
  latitude: number | string
  /**
   * 
   * @type {number | string}
   * @memberof AddressBodyModel
   */
  longitude: number | string
  /**
   * 
   * @type {string}
   * @memberof AddressBodyModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof AddressBodyModel
   */
  street: string
}
/**
 * 
 * @export
 * @interface AddressResponseIsLinkedToVenueModel
 */
export interface AddressResponseIsLinkedToVenueModel {
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  banId?: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  departmentCode?: string
  /**
   * 
   * @type {number}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  id: number
  /**
   * 
   * @type {number}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  id_oa: number
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  inseeCode?: string
  /**
   * 
   * @type {boolean}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  isLinkedToVenue?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  isManualEdition: boolean
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  label?: string
  /**
   * 
   * @type {number}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  latitude: number
  /**
   * 
   * @type {number}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  longitude: number
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseIsLinkedToVenueModel
   */
  street?: string
}
/**
 * 
 * @export
 * @interface AddressResponseModel
 */
export interface AddressResponseModel {
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  banId?: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  departmentCode?: string
  /**
   * 
   * @type {number}
   * @memberof AddressResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  inseeCode?: string
  /**
   * 
   * @type {number}
   * @memberof AddressResponseModel
   */
  latitude: number
  /**
   * 
   * @type {number}
   * @memberof AddressResponseModel
   */
  longitude: number
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof AddressResponseModel
   */
  street?: string
}
/**
 * 
 * @export
 * @interface AggregatedRevenue
 */
export interface AggregatedRevenue {
  /**
   * 
   * @type {CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue}
   * @memberof AggregatedRevenue
   */
  expectedRevenue: CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue
  /**
   * 
   * @type {CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue}
   * @memberof AggregatedRevenue
   */
  revenue: CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue
}
/**
 * 
 * @export
 * @interface AttachImageFormModel
 */
export interface AttachImageFormModel {
  /**
   * 
   * @type {string}
   * @memberof AttachImageFormModel
   */
  credit: string
  /**
   * 
   * @type {number}
   * @memberof AttachImageFormModel
   */
  croppingRectHeight: number
  /**
   * 
   * @type {number}
   * @memberof AttachImageFormModel
   */
  croppingRectWidth: number
  /**
   * 
   * @type {number}
   * @memberof AttachImageFormModel
   */
  croppingRectX: number
  /**
   * 
   * @type {number}
   * @memberof AttachImageFormModel
   */
  croppingRectY: number
}
/**
 * 
 * @export
 * @interface AttachImageResponseModel
 */
export interface AttachImageResponseModel {
  /**
   * 
   * @type {string}
   * @memberof AttachImageResponseModel
   */
  imageUrl: string
}
/**
 * 
 * @export
 * @interface AudioDisabilityModel
 */
export interface AudioDisabilityModel {
  /**
   * 
   * @type {Array<string>}
   * @memberof AudioDisabilityModel
   */
  deafAndHardOfHearing?: Array<string>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BankAccountApplicationStatus {
  EnConstruction = <any> 'en_construction',
  EnInstruction = <any> 'en_instruction',
  Accepte = <any> 'accepte',
  Refuse = <any> 'refuse',
  SansSuite = <any> 'sans_suite',
  ACorriger = <any> 'a_corriger'
}
/**
 * 
 * @export
 * @interface BankAccountResponseModel
 */
export interface BankAccountResponseModel {
  /**
   * 
   * @type {string}
   * @memberof BankAccountResponseModel
   */
  bic: string
  /**
   * 
   * @type {string}
   * @memberof BankAccountResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof BankAccountResponseModel
   */
  dateLastStatusUpdate?: string
  /**
   * 
   * @type {number}
   * @memberof BankAccountResponseModel
   */
  dsApplicationId?: number
  /**
   * 
   * @type {number}
   * @memberof BankAccountResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof BankAccountResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {string}
   * @memberof BankAccountResponseModel
   */
  label: string
  /**
   * 
   * @type {Array<LinkedVenues>}
   * @memberof BankAccountResponseModel
   */
  linkedVenues: Array<LinkedVenues>
  /**
   * 
   * @type {string}
   * @memberof BankAccountResponseModel
   */
  obfuscatedIban: string
  /**
   * 
   * @type {BankAccountApplicationStatus}
   * @memberof BankAccountResponseModel
   */
  status: BankAccountApplicationStatus
}
/**
 * 
 * @export
 * @interface BannerMetaModel
 */
export interface BannerMetaModel {
  /**
   * 
   * @type {CropParams}
   * @memberof BannerMetaModel
   */
  crop_params?: CropParams
  /**
   * 
   * @type {string}
   * @memberof BannerMetaModel
   */
  image_credit?: string
  /**
   * 
   * @type {string}
   * @memberof BannerMetaModel
   */
  original_image_url?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BookingExportType {
  Csv = <any> 'csv',
  Excel = <any> 'excel'
}
/**
 * 
 * @export
 * @interface BookingRecapResponseBeneficiaryModel
 */
export interface BookingRecapResponseBeneficiaryModel {
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseBeneficiaryModel
   */
  email?: string
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseBeneficiaryModel
   */
  firstname?: string
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseBeneficiaryModel
   */
  lastname?: string
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseBeneficiaryModel
   */
  phonenumber?: string
}
/**
 * 
 * @export
 * @interface BookingRecapResponseBookingStatusHistoryModel
 */
export interface BookingRecapResponseBookingStatusHistoryModel {
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseBookingStatusHistoryModel
   */
  date?: string
  /**
   * 
   * @type {BookingRecapStatus}
   * @memberof BookingRecapResponseBookingStatusHistoryModel
   */
  status: BookingRecapStatus
}
/**
 * 
 * @export
 * @interface BookingRecapResponseModel
 */
export interface BookingRecapResponseModel {
  /**
   * 
   * @type {BookingRecapResponseBeneficiaryModel}
   * @memberof BookingRecapResponseModel
   */
  beneficiary: BookingRecapResponseBeneficiaryModel
  /**
   * 
   * @type {number}
   * @memberof BookingRecapResponseModel
   */
  bookingAmount: number
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseModel
   */
  bookingDate: string
  /**
   * 
   * @type {boolean}
   * @memberof BookingRecapResponseModel
   */
  bookingIsDuo: boolean
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseModel
   */
  bookingPriceCategoryLabel?: string
  /**
   * 
   * @type {BookingRecapStatus}
   * @memberof BookingRecapResponseModel
   */
  bookingStatus: BookingRecapStatus
  /**
   * 
   * @type {Array<BookingRecapResponseBookingStatusHistoryModel>}
   * @memberof BookingRecapResponseModel
   */
  bookingStatusHistory: Array<BookingRecapResponseBookingStatusHistoryModel>
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseModel
   */
  bookingToken?: string
  /**
   * 
   * @type {BookingRecapResponseStockModel}
   * @memberof BookingRecapResponseModel
   */
  stock: BookingRecapResponseStockModel
}
/**
 * 
 * @export
 * @interface BookingRecapResponseStockModel
 */
export interface BookingRecapResponseStockModel {
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseStockModel
   */
  eventBeginningDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof BookingRecapResponseStockModel
   */
  offerId: number
  /**
   * 
   * @type {boolean}
   * @memberof BookingRecapResponseStockModel
   */
  offerIsEducational: boolean
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseStockModel
   */
  offerIsbn?: string
  /**
   * 
   * @type {string}
   * @memberof BookingRecapResponseStockModel
   */
  offerName: string
  /**
   * 
   * @type {number}
   * @memberof BookingRecapResponseStockModel
   */
  stockIdentifier: number
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BookingRecapStatus {
  Booked = <any> 'booked',
  Validated = <any> 'validated',
  Cancelled = <any> 'cancelled',
  Reimbursed = <any> 'reimbursed',
  Confirmed = <any> 'confirmed',
  Pending = <any> 'pending'
}
/**
 * 
 * @export
 * @interface BookingStatusFilter
 */
export interface BookingStatusFilter {
}
/**
 * 
 * @export
 * @interface BookingStatusFilter1
 */
export interface BookingStatusFilter1 {
}
/**
 * 
 * @export
 * @interface BookingStatusFilter2
 */
export interface BookingStatusFilter2 {
}
/**
 * 
 * @export
 * @interface BookingStatusFilter3
 */
export interface BookingStatusFilter3 {
}
/**
 * 
 * @export
 * @interface BookingStatusFilter4
 */
export interface BookingStatusFilter4 {
}
/**
 * 
 * @export
 * @interface BookingStatusFilter5
 */
export interface BookingStatusFilter5 {
}
/**
 * 
 * @export
 * @interface BookingStatusHistoryResponseModel
 */
export interface BookingStatusHistoryResponseModel {
  /**
   * 
   * @type {string}
   * @memberof BookingStatusHistoryResponseModel
   */
  date: string
  /**
   * 
   * @type {string}
   * @memberof BookingStatusHistoryResponseModel
   */
  status: string
}
/**
 * 
 * @export
 * @interface BookingsExportQueryModel
 */
export interface BookingsExportQueryModel {
  /**
   * 
   * @type {string}
   * @memberof BookingsExportQueryModel
   */
  event_date: string
  /**
   * 
   * @type {BookingsExportStatusFilter}
   * @memberof BookingsExportQueryModel
   */
  status: BookingsExportStatusFilter
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BookingsExportStatusFilter {
  Validated = <any> 'validated',
  All = <any> 'all'
}
/**
 * 
 * @export
 * @interface CategoriesResponseModel
 */
export interface CategoriesResponseModel {
  /**
   * 
   * @type {Array<CategoryResponseModel>}
   * @memberof CategoriesResponseModel
   */
  categories: Array<CategoryResponseModel>
  /**
   * 
   * @type {Array<SubcategoryResponseModel>}
   * @memberof CategoriesResponseModel
   */
  subcategories: Array<SubcategoryResponseModel>
}
/**
 * 
 * @export
 * @interface CategoryResponseModel
 */
export interface CategoryResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CategoryResponseModel
   */
  id: string
  /**
   * 
   * @type {boolean}
   * @memberof CategoryResponseModel
   */
  isSelectable: boolean
  /**
   * 
   * @type {string}
   * @memberof CategoryResponseModel
   */
  proLabel: string
}
/**
 * 
 * @export
 * @interface ChangePasswordBodyModel
 */
export interface ChangePasswordBodyModel {
  /**
   * 
   * @type {string}
   * @memberof ChangePasswordBodyModel
   */
  newConfirmationPassword: string
  /**
   * 
   * @type {string}
   * @memberof ChangePasswordBodyModel
   */
  newPassword: string
  /**
   * 
   * @type {string}
   * @memberof ChangePasswordBodyModel
   */
  oldPassword: string
}
/**
 * 
 * @export
 * @interface ChangeProEmailBody
 */
export interface ChangeProEmailBody {
  /**
   * 
   * @type {string}
   * @memberof ChangeProEmailBody
   */
  token: string
}
/**
 * 
 * @export
 * @interface CollectiveAndIndividualRevenue
 */
export interface CollectiveAndIndividualRevenue {
  /**
   * 
   * @type {number}
   * @memberof CollectiveAndIndividualRevenue
   */
  collective: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveAndIndividualRevenue
   */
  individual: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveAndIndividualRevenue
   */
  total: number
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveBookingBankAccountStatus {
  ACCEPTED = <any> 'ACCEPTED',
  DRAFT = <any> 'DRAFT',
  MISSING = <any> 'MISSING',
  REJECTED = <any> 'REJECTED'
}
/**
 * 
 * @export
 * @interface CollectiveBookingByIdResponseModel
 */
export interface CollectiveBookingByIdResponseModel {
  /**
   * 
   * @type {CollectiveBookingBankAccountStatus}
   * @memberof CollectiveBookingByIdResponseModel
   */
  bankAccountStatus: CollectiveBookingBankAccountStatus
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingByIdResponseModel
   */
  beginningDatetime: string
  /**
   * 
   * @type {EducationalInstitutionResponseModel}
   * @memberof CollectiveBookingByIdResponseModel
   */
  educationalInstitution: EducationalInstitutionResponseModel
  /**
   * 
   * @type {CollectiveBookingEducationalRedactorResponseModel}
   * @memberof CollectiveBookingByIdResponseModel
   */
  educationalRedactor: CollectiveBookingEducationalRedactorResponseModel
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingByIdResponseModel
   */
  endDatetime: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveBookingByIdResponseModel
   */
  isCancellable: boolean
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  numberOfTickets: number
  /**
   * 
   * @type {CollectiveOfferOfferVenueResponseModel}
   * @memberof CollectiveBookingByIdResponseModel
   */
  offerVenue: CollectiveOfferOfferVenueResponseModel
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  offererId: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  price: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingByIdResponseModel
   */
  startDatetime: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof CollectiveBookingByIdResponseModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  venueDMSApplicationId?: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingByIdResponseModel
   */
  venueId: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingByIdResponseModel
   */
  venuePostalCode?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveBookingCancellationReasons {
  OFFERER = <any> 'OFFERER',
  BENEFICIARY = <any> 'BENEFICIARY',
  EXPIRED = <any> 'EXPIRED',
  FRAUD = <any> 'FRAUD',
  FRAUDSUSPICION = <any> 'FRAUD_SUSPICION',
  FRAUDINAPPROPRIATE = <any> 'FRAUD_INAPPROPRIATE',
  REFUSEDBYINSTITUTE = <any> 'REFUSED_BY_INSTITUTE',
  REFUSEDBYHEADMASTER = <any> 'REFUSED_BY_HEADMASTER',
  PUBLICAPI = <any> 'PUBLIC_API',
  FINANCEINCIDENT = <any> 'FINANCE_INCIDENT',
  BACKOFFICE = <any> 'BACKOFFICE',
  BACKOFFICEEVENTCANCELLED = <any> 'BACKOFFICE_EVENT_CANCELLED',
  BACKOFFICEOFFERMODIFIED = <any> 'BACKOFFICE_OFFER_MODIFIED',
  BACKOFFICEOFFERWITHWRONGINFORMATION = <any> 'BACKOFFICE_OFFER_WITH_WRONG_INFORMATION',
  BACKOFFICEOFFERERBUSINESSCLOSED = <any> 'BACKOFFICE_OFFERER_BUSINESS_CLOSED',
  OFFERERCONNECTAS = <any> 'OFFERER_CONNECT_AS'
}
/**
 * 
 * @export
 * @interface CollectiveBookingCollectiveStockResponseModel
 */
export interface CollectiveBookingCollectiveStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  eventBeginningDatetime: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  eventEndDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  eventStartDatetime: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  numberOfTickets: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  offerId: number
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  offerIsEducational: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  offerIsbn?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingCollectiveStockResponseModel
   */
  offerName: string
}
/**
 * 
 * @export
 * @interface CollectiveBookingEducationalRedactorResponseModel
 */
export interface CollectiveBookingEducationalRedactorResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingEducationalRedactorResponseModel
   */
  civility?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingEducationalRedactorResponseModel
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingEducationalRedactorResponseModel
   */
  firstName?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingEducationalRedactorResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingEducationalRedactorResponseModel
   */
  lastName?: string
}
/**
 * 
 * @export
 * @interface CollectiveBookingResponseModel
 */
export interface CollectiveBookingResponseModel {
  /**
   * 
   * @type {number}
   * @memberof CollectiveBookingResponseModel
   */
  bookingAmount: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingCancellationLimitDate: string
  /**
   * 
   * @type {CollectiveBookingCancellationReasons}
   * @memberof CollectiveBookingResponseModel
   */
  bookingCancellationReason?: CollectiveBookingCancellationReasons
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingConfirmationDate?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingConfirmationLimitDate: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingDate: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingId: string
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveBookingResponseModel
   */
  bookingIsDuo?: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingStatus: string
  /**
   * 
   * @type {Array<BookingStatusHistoryResponseModel>}
   * @memberof CollectiveBookingResponseModel
   */
  bookingStatusHistory: Array<BookingStatusHistoryResponseModel>
  /**
   * 
   * @type {string}
   * @memberof CollectiveBookingResponseModel
   */
  bookingToken?: string
  /**
   * 
   * @type {EducationalInstitutionResponseModel}
   * @memberof CollectiveBookingResponseModel
   */
  institution: EducationalInstitutionResponseModel
  /**
   * 
   * @type {CollectiveBookingCollectiveStockResponseModel}
   * @memberof CollectiveBookingResponseModel
   */
  stock: CollectiveBookingCollectiveStockResponseModel
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveBookingStatus {
  PENDING = <any> 'PENDING',
  CONFIRMED = <any> 'CONFIRMED',
  USED = <any> 'USED',
  CANCELLED = <any> 'CANCELLED',
  REIMBURSED = <any> 'REIMBURSED'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveBookingStatusFilter {
  Booked = <any> 'booked',
  Validated = <any> 'validated',
  Reimbursed = <any> 'reimbursed'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveOfferAllowedAction {
  EDITDETAILS = <any> 'CAN_EDIT_DETAILS',
  EDITDATES = <any> 'CAN_EDIT_DATES',
  EDITINSTITUTION = <any> 'CAN_EDIT_INSTITUTION',
  EDITDISCOUNT = <any> 'CAN_EDIT_DISCOUNT',
  DUPLICATE = <any> 'CAN_DUPLICATE',
  CANCEL = <any> 'CAN_CANCEL',
  ARCHIVE = <any> 'CAN_ARCHIVE'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveOfferDisplayedStatus {
  ACTIVE = <any> 'ACTIVE',
  PENDING = <any> 'PENDING',
  REJECTED = <any> 'REJECTED',
  PREBOOKED = <any> 'PREBOOKED',
  BOOKED = <any> 'BOOKED',
  INACTIVE = <any> 'INACTIVE',
  EXPIRED = <any> 'EXPIRED',
  ENDED = <any> 'ENDED',
  CANCELLED = <any> 'CANCELLED',
  REIMBURSED = <any> 'REIMBURSED',
  ARCHIVED = <any> 'ARCHIVED',
  DRAFT = <any> 'DRAFT'
}
/**
 * 
 * @export
 * @interface CollectiveOfferInstitutionModel
 */
export interface CollectiveOfferInstitutionModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferInstitutionModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferInstitutionModel
   */
  institutionId: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferInstitutionModel
   */
  institutionType: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferInstitutionModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferInstitutionModel
   */
  postalCode: string
}
/**
 * 
 * @export
 * @interface CollectiveOfferOfferVenueResponseModel
 */
export interface CollectiveOfferOfferVenueResponseModel {
  /**
   * 
   * @type {OfferAddressType}
   * @memberof CollectiveOfferOfferVenueResponseModel
   */
  addressType: OfferAddressType
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenueResponseModel
   */
  otherAddress: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferOfferVenueResponseModel
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface CollectiveOfferRedactorModel
 */
export interface CollectiveOfferRedactorModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferRedactorModel
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferRedactorModel
   */
  firstName?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferRedactorModel
   */
  lastName?: string
}
/**
 * 
 * @export
 * @interface CollectiveOfferResponseIdModel
 */
export interface CollectiveOfferResponseIdModel {
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferResponseIdModel
   */
  id: number
}
/**
 * 
 * @export
 * @interface CollectiveOfferResponseModel
 */
export interface CollectiveOfferResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferAllowedAction> | Array<CollectiveOfferTemplateAllowedAction>}
   * @memberof CollectiveOfferResponseModel
   */
  allowedActions: Array<CollectiveOfferAllowedAction> | Array<CollectiveOfferTemplateAllowedAction>
  /**
   * 
   * @type {CollectiveOffersBookingResponseModel}
   * @memberof CollectiveOfferResponseModel
   */
  booking?: CollectiveOffersBookingResponseModel
  /**
   * 
   * @type {TemplateDatesModel}
   * @memberof CollectiveOfferResponseModel
   */
  dates?: TemplateDatesModel
  /**
   * 
   * @type {CollectiveOfferDisplayedStatus}
   * @memberof CollectiveOfferResponseModel
   */
  displayedStatus: CollectiveOfferDisplayedStatus
  /**
   * 
   * @type {EducationalInstitutionResponseModel}
   * @memberof CollectiveOfferResponseModel
   */
  educationalInstitution?: EducationalInstitutionResponseModel
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof CollectiveOfferResponseModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  imageCredit?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  imageUrl?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof CollectiveOfferResponseModel
   */
  interventionArea: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isEditableByPcPro: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isEducational: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isPublicApi: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isShowcase: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  name: string
  /**
   * 
   * @type {NationalProgramModel}
   * @memberof CollectiveOfferResponseModel
   */
  nationalProgram?: NationalProgramModel
  /**
   * 
   * @type {CollectiveOfferStatus}
   * @memberof CollectiveOfferResponseModel
   */
  status: CollectiveOfferStatus
  /**
   * 
   * @type {Array<CollectiveOffersStockResponseModel>}
   * @memberof CollectiveOfferResponseModel
   */
  stocks: Array<CollectiveOffersStockResponseModel>
  /**
   * 
   * @type {SubcategoryIdEnum | string}
   * @memberof CollectiveOfferResponseModel
   */
  subcategoryId?: SubcategoryIdEnum | string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  templateId?: string
  /**
   * 
   * @type {ListOffersVenueResponseModel}
   * @memberof CollectiveOfferResponseModel
   */
  venue: ListOffersVenueResponseModel
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveOfferStatus {
  ACTIVE = <any> 'ACTIVE',
  PENDING = <any> 'PENDING',
  EXPIRED = <any> 'EXPIRED',
  REJECTED = <any> 'REJECTED',
  SOLDOUT = <any> 'SOLD_OUT',
  INACTIVE = <any> 'INACTIVE',
  DRAFT = <any> 'DRAFT',
  ARCHIVED = <any> 'ARCHIVED'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum CollectiveOfferTemplateAllowedAction {
  EDITDETAILS = <any> 'CAN_EDIT_DETAILS',
  DUPLICATE = <any> 'CAN_DUPLICATE',
  ARCHIVE = <any> 'CAN_ARCHIVE',
  CREATEBOOKABLEOFFER = <any> 'CAN_CREATE_BOOKABLE_OFFER',
  PUBLISH = <any> 'CAN_PUBLISH',
  HIDE = <any> 'CAN_HIDE'
}
/**
 * 
 * @export
 * @interface CollectiveOfferTemplateBodyModel
 */
export interface CollectiveOfferTemplateBodyModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateBodyModel
   */
  educationalPriceDetail?: string
}
/**
 * 
 * @export
 * @interface CollectiveOfferTemplateResponseIdModel
 */
export interface CollectiveOfferTemplateResponseIdModel {
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferTemplateResponseIdModel
   */
  id: number
}
/**
 * 
 * @export
 * @interface CollectiveOfferType
 */
export interface CollectiveOfferType {
}
/**
 * 
 * @export
 * @interface CollectiveOfferType1
 */
export interface CollectiveOfferType1 {
}
/**
 * 
 * @export
 * @interface CollectiveOfferVenueBodyModel
 */
export interface CollectiveOfferVenueBodyModel {
  /**
   * 
   * @type {OfferAddressType}
   * @memberof CollectiveOfferVenueBodyModel
   */
  addressType: OfferAddressType
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferVenueBodyModel
   */
  otherAddress: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferVenueBodyModel
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface CollectiveOffersBookingResponseModel
 */
export interface CollectiveOffersBookingResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOffersBookingResponseModel
   */
  booking_status: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveOffersBookingResponseModel
   */
  id: number
}
/**
 * 
 * @export
 * @interface CollectiveOffersStockResponseModel
 */
export interface CollectiveOffersStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOffersStockResponseModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOffersStockResponseModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOffersStockResponseModel
   */
  endDatetime?: string
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOffersStockResponseModel
   */
  hasBookingLimitDatetimePassed: boolean
  /**
   * 
   * @type {number | string}
   * @memberof CollectiveOffersStockResponseModel
   */
  remainingQuantity: number | string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOffersStockResponseModel
   */
  startDatetime?: string
}
/**
 * 
 * @export
 * @interface CollectiveRevenue
 */
export interface CollectiveRevenue {
  /**
   * 
   * @type {number}
   * @memberof CollectiveRevenue
   */
  collective: number
}
/**
 * 
 * @export
 * @interface CollectiveStockCreationBodyModel
 */
export interface CollectiveStockCreationBodyModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockCreationBodyModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockCreationBodyModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockCreationBodyModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockCreationBodyModel
   */
  endDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockCreationBodyModel
   */
  numberOfTickets: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockCreationBodyModel
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockCreationBodyModel
   */
  startDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockCreationBodyModel
   */
  totalPrice: number
}
/**
 * 
 * @export
 * @interface CollectiveStockEditionBodyModel
 */
export interface CollectiveStockEditionBodyModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockEditionBodyModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockEditionBodyModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockEditionBodyModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockEditionBodyModel
   */
  endDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockEditionBodyModel
   */
  numberOfTickets?: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockEditionBodyModel
   */
  startDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockEditionBodyModel
   */
  totalPrice?: number
}
/**
 * 
 * @export
 * @interface CollectiveStockResponseModel
 */
export interface CollectiveStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockResponseModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockResponseModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockResponseModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockResponseModel
   */
  endDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveStockResponseModel
   */
  isEducationalStockEditable: boolean
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockResponseModel
   */
  numberOfTickets?: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveStockResponseModel
   */
  price: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveStockResponseModel
   */
  startDatetime?: string
}
/**
 * 
 * @export
 * @interface CombinedInvoiceListModel
 */
export interface CombinedInvoiceListModel {
  /**
   * 
   * @type {Array<string>}
   * @memberof CombinedInvoiceListModel
   */
  invoiceReferences: Array<string>
}
/**
 * 
 * @export
 * @interface Consent
 */
export interface Consent {
  /**
   * 
   * @type {Array<string>}
   * @memberof Consent
   */
  accepted: Array<string>
  /**
   * 
   * @type {Array<string>}
   * @memberof Consent
   */
  mandatory: Array<string>
  /**
   * 
   * @type {Array<string>}
   * @memberof Consent
   */
  refused: Array<string>
}
/**
 * 
 * @export
 * @interface CookieConsentRequest
 */
export interface CookieConsentRequest {
  /**
   * 
   * @type {string}
   * @memberof CookieConsentRequest
   */
  choiceDatetime: string
  /**
   * 
   * @type {Consent}
   * @memberof CookieConsentRequest
   */
  consent: Consent
  /**
   * 
   * @type {string}
   * @memberof CookieConsentRequest
   */
  deviceId: string
  /**
   * 
   * @type {number}
   * @memberof CookieConsentRequest
   */
  userId?: number
}
/**
 * 
 * @export
 * @interface CreateOffererQueryModel
 */
export interface CreateOffererQueryModel {
  /**
   * 
   * @type {string}
   * @memberof CreateOffererQueryModel
   */
  city: string
  /**
   * 
   * @type {number}
   * @memberof CreateOffererQueryModel
   */
  latitude?: number
  /**
   * 
   * @type {number}
   * @memberof CreateOffererQueryModel
   */
  longitude?: number
  /**
   * 
   * @type {string}
   * @memberof CreateOffererQueryModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof CreateOffererQueryModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof CreateOffererQueryModel
   */
  siren: string
  /**
   * 
   * @type {string}
   * @memberof CreateOffererQueryModel
   */
  street?: string
}
/**
 * 
 * @export
 * @interface CreatePriceCategoryModel
 */
export interface CreatePriceCategoryModel {
  /**
   * 
   * @type {string}
   * @memberof CreatePriceCategoryModel
   */
  label: string
  /**
   * 
   * @type {number}
   * @memberof CreatePriceCategoryModel
   */
  price: number
}
/**
 * 
 * @export
 * @interface CreateThumbnailBodyModel
 */
export interface CreateThumbnailBodyModel {
  /**
   * 
   * @type {string}
   * @memberof CreateThumbnailBodyModel
   */
  credit?: string
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailBodyModel
   */
  croppingRectHeight?: number
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailBodyModel
   */
  croppingRectWidth?: number
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailBodyModel
   */
  croppingRectX?: number
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailBodyModel
   */
  croppingRectY?: number
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailBodyModel
   */
  offerId: number
}
/**
 * 
 * @export
 * @interface CreateThumbnailResponseModel
 */
export interface CreateThumbnailResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CreateThumbnailResponseModel
   */
  credit?: string
  /**
   * 
   * @type {number}
   * @memberof CreateThumbnailResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CreateThumbnailResponseModel
   */
  url: string
}
/**
 * 
 * @export
 * @interface CropParams
 */
export interface CropParams {
  /**
   * 
   * @type {number}
   * @memberof CropParams
   */
  height_crop_percent?: number
  /**
   * 
   * @type {number}
   * @memberof CropParams
   */
  width_crop_percent?: number
  /**
   * 
   * @type {number}
   * @memberof CropParams
   */
  x_crop_percent?: number
  /**
   * 
   * @type {number}
   * @memberof CropParams
   */
  y_crop_percent?: number
}
/**
 * 
 * @export
 * @interface CulturalPartner
 */
export interface CulturalPartner {
  /**
   * 
   * @type {string}
   * @memberof CulturalPartner
   */
  communeLibelle?: string
  /**
   * 
   * @type {number}
   * @memberof CulturalPartner
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CulturalPartner
   */
  libelle: string
  /**
   * 
   * @type {string}
   * @memberof CulturalPartner
   */
  regionLibelle?: string
}
/**
 * 
 * @export
 * @interface DMSApplicationForEAC
 */
export interface DMSApplicationForEAC {
  /**
   * 
   * @type {number}
   * @memberof DMSApplicationForEAC
   */
  application: number
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  buildDate?: string
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  depositDate: string
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  expirationDate?: string
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  instructionDate?: string
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  lastChangeDate: string
  /**
   * 
   * @type {number}
   * @memberof DMSApplicationForEAC
   */
  procedure: number
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  processingDate?: string
  /**
   * 
   * @type {DMSApplicationstatus}
   * @memberof DMSApplicationForEAC
   */
  state: DMSApplicationstatus
  /**
   * 
   * @type {string}
   * @memberof DMSApplicationForEAC
   */
  userDeletionDate?: string
  /**
   * 
   * @type {number}
   * @memberof DMSApplicationForEAC
   */
  venueId: number
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum DMSApplicationstatus {
  Accepte = <any> 'accepte',
  SansSuite = <any> 'sans_suite',
  EnConstruction = <any> 'en_construction',
  Refuse = <any> 'refuse',
  EnInstruction = <any> 'en_instruction'
}
/**
 * 
 * @export
 * @interface DateRangeModel
 */
export interface DateRangeModel {
  /**
   * 
   * @type {string}
   * @memberof DateRangeModel
   */
  end: string
  /**
   * 
   * @type {string}
   * @memberof DateRangeModel
   */
  start: string
}
/**
 * 
 * @export
 * @interface DateRangeOnCreateModel
 */
export interface DateRangeOnCreateModel {
  /**
   * 
   * @type {string}
   * @memberof DateRangeOnCreateModel
   */
  end: string
  /**
   * 
   * @type {string}
   * @memberof DateRangeOnCreateModel
   */
  start: string
}
/**
 * 
 * @export
 * @interface DeleteFilteredStockListBody
 */
export interface DeleteFilteredStockListBody {
  /**
   * 
   * @type {string}
   * @memberof DeleteFilteredStockListBody
   */
  date?: string
  /**
   * 
   * @type {number}
   * @memberof DeleteFilteredStockListBody
   */
  price_category_id?: number
  /**
   * 
   * @type {string}
   * @memberof DeleteFilteredStockListBody
   */
  time?: string
}
/**
 * 
 * @export
 * @interface DeleteOfferRequestBody
 */
export interface DeleteOfferRequestBody {
  /**
   * 
   * @type {Array<number>}
   * @memberof DeleteOfferRequestBody
   */
  ids: Array<number>
}
/**
 * 
 * @export
 * @interface DeleteStockListBody
 */
export interface DeleteStockListBody {
  /**
   * 
   * @type {Array<number>}
   * @memberof DeleteStockListBody
   */
  ids_to_delete: Array<number>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum EacFormat {
  AtelierDePratique = <any> 'Atelier de pratique',
  Concert = <any> 'Concert',
  ConfrenceRencontre = <any> 'Conférence, rencontre',
  FestivalSalonCongrs = <any> 'Festival, salon, congrès',
  ProjectionAudiovisuelle = <any> 'Projection audiovisuelle',
  Reprsentation = <any> 'Représentation',
  VisiteGuide = <any> 'Visite guidée',
  VisiteLibre = <any> 'Visite libre'
}
/**
 * 
 * @export
 * @interface EditPriceCategoryModel
 */
export interface EditPriceCategoryModel {
  /**
   * 
   * @type {number}
   * @memberof EditPriceCategoryModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof EditPriceCategoryModel
   */
  label?: string
  /**
   * 
   * @type {number}
   * @memberof EditPriceCategoryModel
   */
  price?: number
}
/**
 * 
 * @export
 * @interface EditVenueBodyModel
 */
export interface EditVenueBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  banId?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  city?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  comment?: string
  /**
   * 
   * @type {VenueContactModel}
   * @memberof EditVenueBodyModel
   */
  contact?: VenueContactModel
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  description?: string
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  isAccessibilityAppliedOnAllOffers?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  isManualEdition?: boolean
  /**
   * 
   * @type {number | string}
   * @memberof EditVenueBodyModel
   */
  latitude?: number | string
  /**
   * 
   * @type {number | string}
   * @memberof EditVenueBodyModel
   */
  longitude?: number | string
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  name?: string
  /**
   * 
   * @type {Array<OpeningHoursModel>}
   * @memberof EditVenueBodyModel
   */
  openingHours?: Array<OpeningHoursModel>
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  siret?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  street?: string
  /**
   * 
   * @type {number}
   * @memberof EditVenueBodyModel
   */
  venueLabelId?: number
  /**
   * 
   * @type {VenueTypeCode}
   * @memberof EditVenueBodyModel
   */
  venueTypeCode?: VenueTypeCode
  /**
   * 
   * @type {boolean}
   * @memberof EditVenueBodyModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof EditVenueBodyModel
   */
  withdrawalDetails?: string
}
/**
 * 
 * @export
 * @interface EditVenueCollectiveDataBodyModel
 */
export interface EditVenueCollectiveDataBodyModel {
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveAccessInformation?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveDescription?: string
  /**
   * 
   * @type {Array<number>}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveDomains?: Array<number>
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveEmail?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveInterventionArea?: Array<string>
  /**
   * 
   * @type {Array<string>}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveNetwork?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectivePhone?: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveStudents?: Array<StudentLevels>
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveSubCategoryId?: string
  /**
   * 
   * @type {string}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  collectiveWebsite?: string
  /**
   * 
   * @type {number}
   * @memberof EditVenueCollectiveDataBodyModel
   */
  venueEducationalStatusId?: number
}
/**
 * 
 * @export
 * @interface EducationalDomainResponseModel
 */
export interface EducationalDomainResponseModel {
  /**
   * 
   * @type {number}
   * @memberof EducationalDomainResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof EducationalDomainResponseModel
   */
  name: string
}
/**
 * 
 * @export
 */
export type EducationalDomainsResponseModel = Array<EducationalDomainResponseModel>
/**
 * 
 * @export
 * @interface EducationalInstitutionResponseModel
 */
export interface EducationalInstitutionResponseModel {
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  city: string
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  institutionId: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  institutionType?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  phoneNumber: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionResponseModel
   */
  postalCode: string
}
/**
 * 
 * @export
 * @interface EducationalInstitutionsQueryModel
 */
export interface EducationalInstitutionsQueryModel {
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionsQueryModel
   */
  page?: number
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionsQueryModel
   */
  perPageLimit?: number
}
/**
 * 
 * @export
 * @interface EducationalInstitutionsResponseModel
 */
export interface EducationalInstitutionsResponseModel {
  /**
   * 
   * @type {Array<EducationalInstitutionResponseModel>}
   * @memberof EducationalInstitutionsResponseModel
   */
  educationalInstitutions: Array<EducationalInstitutionResponseModel>
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionsResponseModel
   */
  page: number
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionsResponseModel
   */
  pages: number
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionsResponseModel
   */
  total: number
}
/**
 * 
 * @export
 * @interface EducationalRedactor
 */
export interface EducationalRedactor {
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactor
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactor
   */
  gender?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactor
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactor
   */
  surname: string
}
/**
 * 
 * @export
 * @interface EducationalRedactorQueryModel
 */
export interface EducationalRedactorQueryModel {
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorQueryModel
   */
  candidate: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorQueryModel
   */
  uai: string
}
/**
 * 
 * @export
 * @interface EducationalRedactorResponseModel
 */
export interface EducationalRedactorResponseModel {
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorResponseModel
   */
  civility?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorResponseModel
   */
  email?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorResponseModel
   */
  firstName?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalRedactorResponseModel
   */
  lastName?: string
}
/**
 * 
 * @export
 */
export type EducationalRedactors = Array<EducationalRedactor>
/**
 * 
 * @export
 * @interface EventDateScheduleAndPriceCategoriesCountModel
 */
export interface EventDateScheduleAndPriceCategoriesCountModel {
  /**
   * 
   * @type {string}
   * @memberof EventDateScheduleAndPriceCategoriesCountModel
   */
  eventDate: string
  /**
   * 
   * @type {number}
   * @memberof EventDateScheduleAndPriceCategoriesCountModel
   */
  priceCategoriesCount: number
  /**
   * 
   * @type {number}
   * @memberof EventDateScheduleAndPriceCategoriesCountModel
   */
  scheduleCount: number
}
/**
 * 
 * @export
 */
export type EventDatesInfos = Array<EventDateScheduleAndPriceCategoriesCountModel>
/**
 * 
 * @export
 * @interface ExportType
 */
export interface ExportType {
}
/**
 * 
 * @export
 * @interface ExportType1
 */
export interface ExportType1 {
}
/**
 * 
 * @export
 * @interface ExportType2
 */
export interface ExportType2 {
}
/**
 * 
 * @export
 * @interface ExternalAccessibilityDataModel
 */
export interface ExternalAccessibilityDataModel {
  /**
   * 
   * @type {AudioDisabilityModel}
   * @memberof ExternalAccessibilityDataModel
   */
  audioDisability?: AudioDisabilityModel
  /**
   * 
   * @type {boolean}
   * @memberof ExternalAccessibilityDataModel
   */
  isAccessibleAudioDisability?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ExternalAccessibilityDataModel
   */
  isAccessibleMentalDisability?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ExternalAccessibilityDataModel
   */
  isAccessibleMotorDisability?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ExternalAccessibilityDataModel
   */
  isAccessibleVisualDisability?: boolean
  /**
   * 
   * @type {MentalDisabilityModel}
   * @memberof ExternalAccessibilityDataModel
   */
  mentalDisability?: MentalDisabilityModel
  /**
   * 
   * @type {MotorDisabilityModel}
   * @memberof ExternalAccessibilityDataModel
   */
  motorDisability?: MotorDisabilityModel
  /**
   * 
   * @type {VisualDisabilityModel}
   * @memberof ExternalAccessibilityDataModel
   */
  visualDisability?: VisualDisabilityModel
}
/**
 * 
 * @export
 * @interface FeatureResponseModel
 */
export interface FeatureResponseModel {
  /**
   * 
   * @type {string}
   * @memberof FeatureResponseModel
   */
  description: string
  /**
   * 
   * @type {string}
   * @memberof FeatureResponseModel
   */
  id: string
  /**
   * 
   * @type {boolean}
   * @memberof FeatureResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {string}
   * @memberof FeatureResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof FeatureResponseModel
   */
  nameKey: string
}
/**
 * 
 * @export
 */
export type FinanceBankAccountListResponseModel = Array<FinanceBankAccountResponseModel>
/**
 * 
 * @export
 * @interface FinanceBankAccountResponseModel
 */
export interface FinanceBankAccountResponseModel {
  /**
   * 
   * @type {number}
   * @memberof FinanceBankAccountResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof FinanceBankAccountResponseModel
   */
  label: string
}
/**
 * 
 * @export
 * @interface Format
 */
export interface Format {
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum GenderEnum {
  M = <any> 'M.',
  Mme = <any> 'Mme'
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferCollectiveStockResponseModel
 */
export interface GetCollectiveOfferCollectiveStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  endDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  isBooked: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  isCancellable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  isEducationalStockEditable: boolean
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  numberOfTickets?: number
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  price: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferCollectiveStockResponseModel
   */
  startDatetime?: string
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferManagingOffererResponseModel
 */
export interface GetCollectiveOfferManagingOffererResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferManagingOffererResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferManagingOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferManagingOffererResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferManagingOffererResponseModel
   */
  siren?: string
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferProviderResponseModel
 */
export interface GetCollectiveOfferProviderResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferProviderResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferRequestResponseModel
 */
export interface GetCollectiveOfferRequestResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  comment: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  dateCreated?: string
  /**
   * 
   * @type {CollectiveOfferInstitutionModel}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  institution: CollectiveOfferInstitutionModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {CollectiveOfferRedactorModel}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  redactor: CollectiveOfferRedactorModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  requestedDate?: string
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  totalStudents?: number
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferRequestResponseModel
   */
  totalTeachers?: number
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferResponseModel
 */
export interface GetCollectiveOfferResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferAllowedAction>}
   * @memberof GetCollectiveOfferResponseModel
   */
  allowedActions: Array<CollectiveOfferAllowedAction>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof GetCollectiveOfferResponseModel
   */
  bookingEmails: Array<string>
  /**
   * 
   * @type {GetCollectiveOfferCollectiveStockResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  contactEmail?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {TemplateDatesModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  dates?: TemplateDatesModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  description: string
  /**
   * 
   * @type {CollectiveOfferDisplayedStatus}
   * @memberof GetCollectiveOfferResponseModel
   */
  displayedStatus: CollectiveOfferDisplayedStatus
  /**
   * 
   * @type {Array<OfferDomain>}
   * @memberof GetCollectiveOfferResponseModel
   */
  domains: Array<OfferDomain>
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof GetCollectiveOfferResponseModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  imageCredit?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  imageUrl?: string
  /**
   * 
   * @type {EducationalInstitutionResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  institution?: EducationalInstitutionResponseModel
  /**
   * 
   * @type {Array<string>}
   * @memberof GetCollectiveOfferResponseModel
   */
  interventionArea: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isBookable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isCancellable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isNonFreeOffer?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isPublicApi: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isTemplate?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  isVisibilityEditable: boolean
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferResponseModel
   */
  lastBookingId?: number
  /**
   * 
   * @type {CollectiveBookingStatus}
   * @memberof GetCollectiveOfferResponseModel
   */
  lastBookingStatus?: CollectiveBookingStatus
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferResponseModel
   */
  name: string
  /**
   * 
   * @type {NationalProgramModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  nationalProgram?: NationalProgramModel
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferResponseModel
   */
  offerId?: number
  /**
   * 
   * @type {CollectiveOfferOfferVenueResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  offerVenue: CollectiveOfferOfferVenueResponseModel
  /**
   * 
   * @type {GetCollectiveOfferProviderResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  provider?: GetCollectiveOfferProviderResponseModel
  /**
   * 
   * @type {CollectiveOfferStatus}
   * @memberof GetCollectiveOfferResponseModel
   */
  status: CollectiveOfferStatus
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof GetCollectiveOfferResponseModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {SubcategoryIdEnum | string}
   * @memberof GetCollectiveOfferResponseModel
   */
  subcategoryId?: SubcategoryIdEnum | string
  /**
   * 
   * @type {EducationalRedactorResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  teacher?: EducationalRedactorResponseModel
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferResponseModel
   */
  templateId?: number
  /**
   * 
   * @type {GetCollectiveOfferVenueResponseModel}
   * @memberof GetCollectiveOfferResponseModel
   */
  venue: GetCollectiveOfferVenueResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferTemplateResponseModel
 */
export interface GetCollectiveOfferTemplateResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferTemplateAllowedAction>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  bookingEmails: Array<string>
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  contactEmail?: string
  /**
   * 
   * @type {OfferContactFormEnum}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  contactForm?: OfferContactFormEnum
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  contactUrl?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {TemplateDatesModel}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  dates?: TemplateDatesModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  description: string
  /**
   * 
   * @type {CollectiveOfferDisplayedStatus}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  displayedStatus: CollectiveOfferDisplayedStatus
  /**
   * 
   * @type {Array<OfferDomain>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  domains: Array<OfferDomain>
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  imageCredit?: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  imageUrl?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  interventionArea: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  isCancellable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  isNonFreeOffer?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  isTemplate?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  name: string
  /**
   * 
   * @type {NationalProgramModel}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  nationalProgram?: NationalProgramModel
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  offerId?: number
  /**
   * 
   * @type {CollectiveOfferOfferVenueResponseModel}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  offerVenue: CollectiveOfferOfferVenueResponseModel
  /**
   * 
   * @type {CollectiveOfferStatus}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  status: CollectiveOfferStatus
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {SubcategoryIdEnum | string}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  subcategoryId?: SubcategoryIdEnum | string
  /**
   * 
   * @type {GetCollectiveOfferVenueResponseModel}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  venue: GetCollectiveOfferVenueResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetCollectiveOfferTemplateResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface GetCollectiveOfferVenueResponseModel
 */
export interface GetCollectiveOfferVenueResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {number}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  imgUrl?: string
  /**
   * 
   * @type {GetCollectiveOfferManagingOffererResponseModel}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  managingOfferer: GetCollectiveOfferManagingOffererResponseModel
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetCollectiveOfferVenueResponseModel
   */
  publicName?: string
}
/**
 * 
 * @export
 * @interface GetEducationalOffererResponseModel
 */
export interface GetEducationalOffererResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {number}
   * @memberof GetEducationalOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {Array<GetEducationalOffererVenueResponseModel>}
   * @memberof GetEducationalOffererResponseModel
   */
  managedVenues: Array<GetEducationalOffererVenueResponseModel>
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetEducationalOffererVenueResponseModel
 */
export interface GetEducationalOffererVenueResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  city?: string
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  collectiveEmail?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  collectiveInterventionArea?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  collectivePhone?: string
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  collectiveSubCategoryId?: string
  /**
   * 
   * @type {number}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  street?: string
  /**
   * 
   * @type {boolean}
   * @memberof GetEducationalOffererVenueResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface GetEducationalOfferersQueryModel
 */
export interface GetEducationalOfferersQueryModel {
  /**
   * 
   * @type {number}
   * @memberof GetEducationalOfferersQueryModel
   */
  offerer_id?: number
}
/**
 * 
 * @export
 * @interface GetEducationalOfferersResponseModel
 */
export interface GetEducationalOfferersResponseModel {
  /**
   * 
   * @type {Array<GetEducationalOffererResponseModel>}
   * @memberof GetEducationalOfferersResponseModel
   */
  educationalOfferers: Array<GetEducationalOffererResponseModel>
}
/**
 * 
 * @export
 * @interface GetIndividualOfferResponseModel
 */
export interface GetIndividualOfferResponseModel {
  /**
   * 
   * @type {GetOfferMediationResponseModel}
   * @memberof GetIndividualOfferResponseModel
   */
  activeMediation?: GetOfferMediationResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  bookingContact?: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferResponseModel
   */
  bookingsCount?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  externalTicketOfficeUrl?: string
  /**
   * 
   * @type {any}
   * @memberof GetIndividualOfferResponseModel
   */
  extraData?: any
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  hasStocks: boolean
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isActivable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isDigital: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isDuo: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isEvent: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isNational: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isNonFreeOffer?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  isThing: boolean
  /**
   * 
   * @type {GetOfferLastProviderResponseModel}
   * @memberof GetIndividualOfferResponseModel
   */
  lastProvider?: GetOfferLastProviderResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  name: string
  /**
   * 
   * @type {Array<PriceCategoryResponseModel>}
   * @memberof GetIndividualOfferResponseModel
   */
  priceCategories?: Array<PriceCategoryResponseModel>
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferResponseModel
   */
  productId?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  publicationDate?: string
  /**
   * 
   * @type {OfferStatus}
   * @memberof GetIndividualOfferResponseModel
   */
  status: OfferStatus
  /**
   * 
   * @type {SubcategoryIdEnum}
   * @memberof GetIndividualOfferResponseModel
   */
  subcategoryId: SubcategoryIdEnum
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  thumbUrl?: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  url?: string
  /**
   * 
   * @type {GetOfferVenueResponseModel}
   * @memberof GetIndividualOfferResponseModel
   */
  venue: GetOfferVenueResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferResponseModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferResponseModel
   */
  withdrawalDelay?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferResponseModel
   */
  withdrawalDetails?: string
  /**
   * 
   * @type {WithdrawalTypeEnum}
   * @memberof GetIndividualOfferResponseModel
   */
  withdrawalType?: WithdrawalTypeEnum
}
/**
 * 
 * @export
 * @interface GetIndividualOfferWithAddressResponseModel
 */
export interface GetIndividualOfferWithAddressResponseModel {
  /**
   * 
   * @type {GetOfferMediationResponseModel}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  activeMediation?: GetOfferMediationResponseModel
  /**
   * 
   * @type {AddressResponseIsLinkedToVenueModel}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  address?: AddressResponseIsLinkedToVenueModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  bookingContact?: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  bookingsCount?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  externalTicketOfficeUrl?: string
  /**
   * 
   * @type {any}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  extraData?: any
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  hasPendingBookings: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  hasStocks: boolean
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isActivable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isDigital: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isDuo: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isEvent: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isNational: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isNonFreeOffer?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  isThing: boolean
  /**
   * 
   * @type {GetOfferLastProviderResponseModel}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  lastProvider?: GetOfferLastProviderResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  name: string
  /**
   * 
   * @type {Array<PriceCategoryResponseModel>}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  priceCategories?: Array<PriceCategoryResponseModel>
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  productId?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  publicationDate?: string
  /**
   * 
   * @type {OfferStatus}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  status: OfferStatus
  /**
   * 
   * @type {SubcategoryIdEnum}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  subcategoryId: SubcategoryIdEnum
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  thumbUrl?: string
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  url?: string
  /**
   * 
   * @type {GetOfferVenueResponseModel}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  venue: GetOfferVenueResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {number}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  withdrawalDelay?: number
  /**
   * 
   * @type {string}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  withdrawalDetails?: string
  /**
   * 
   * @type {WithdrawalTypeEnum}
   * @memberof GetIndividualOfferWithAddressResponseModel
   */
  withdrawalType?: WithdrawalTypeEnum
}
/**
 * 
 * @export
 */
export type GetMusicTypesResponse = Array<MusicTypeResponse>
/**
 * 
 * @export
 * @interface GetOfferLastProviderResponseModel
 */
export interface GetOfferLastProviderResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOfferLastProviderResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetOfferManagingOffererResponseModel
 */
export interface GetOfferManagingOffererResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferManagingOffererResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOfferManagingOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetOfferManagingOffererResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetOfferMediationResponseModel
 */
export interface GetOfferMediationResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOfferMediationResponseModel
   */
  authorId?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferMediationResponseModel
   */
  credit?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferMediationResponseModel
   */
  thumbUrl?: string
}
/**
 * 
 * @export
 * @interface GetOfferStockResponseModel
 */
export interface GetOfferStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOfferStockResponseModel
   */
  activationCodesExpirationDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferStockResponseModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferStockResponseModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof GetOfferStockResponseModel
   */
  bookingsQuantity: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferStockResponseModel
   */
  hasActivationCode: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOfferStockResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferStockResponseModel
   */
  isEventDeletable: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOfferStockResponseModel
   */
  price: number
  /**
   * 
   * @type {number}
   * @memberof GetOfferStockResponseModel
   */
  priceCategoryId?: number
  /**
   * 
   * @type {number}
   * @memberof GetOfferStockResponseModel
   */
  quantity?: number
  /**
   * 
   * @type {number | string}
   * @memberof GetOfferStockResponseModel
   */
  remainingQuantity?: number | string
}
/**
 * 
 * @export
 * @interface GetOfferVenueResponseModel
 */
export interface GetOfferVenueResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferVenueResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  city?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {number}
   * @memberof GetOfferVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferVenueResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {GetOfferManagingOffererResponseModel}
   * @memberof GetOfferVenueResponseModel
   */
  managingOfferer: GetOfferManagingOffererResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferVenueResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferVenueResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof GetOfferVenueResponseModel
   */
  street?: string
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferVenueResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface GetOffererAddressResponseModel
 */
export interface GetOffererAddressResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOffererAddressResponseModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererAddressResponseModel
   */
  departmentCode?: string
  /**
   * 
   * @type {number}
   * @memberof GetOffererAddressResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererAddressResponseModel
   */
  isLinkedToVenue: boolean
  /**
   * 
   * @type {string}
   * @memberof GetOffererAddressResponseModel
   */
  label?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererAddressResponseModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererAddressResponseModel
   */
  street?: string
}
/**
 * 
 * @export
 * @interface GetOffererAddressesQueryModel
 */
export interface GetOffererAddressesQueryModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererAddressesQueryModel
   */
  onlyWithOffers?: boolean
}
/**
 * 
 * @export
 */
export type GetOffererAddressesResponseModel = Array<GetOffererAddressResponseModel>
/**
 * 
 * @export
 * @interface GetOffererBankAccountsResponseModel
 */
export interface GetOffererBankAccountsResponseModel {
  /**
   * 
   * @type {Array<BankAccountResponseModel>}
   * @memberof GetOffererBankAccountsResponseModel
   */
  bankAccounts: Array<BankAccountResponseModel>
  /**
   * 
   * @type {number}
   * @memberof GetOffererBankAccountsResponseModel
   */
  id: number
  /**
   * 
   * @type {Array<ManagedVenues>}
   * @memberof GetOffererBankAccountsResponseModel
   */
  managedVenues: Array<ManagedVenues>
}
/**
 * 
 * @export
 * @interface GetOffererMemberResponseModel
 */
export interface GetOffererMemberResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOffererMemberResponseModel
   */
  email: string
  /**
   * 
   * @type {OffererMemberStatus}
   * @memberof GetOffererMemberResponseModel
   */
  status: OffererMemberStatus
}
/**
 * 
 * @export
 * @interface GetOffererMembersResponseModel
 */
export interface GetOffererMembersResponseModel {
  /**
   * 
   * @type {Array<GetOffererMemberResponseModel>}
   * @memberof GetOffererMembersResponseModel
   */
  members: Array<GetOffererMemberResponseModel>
}
/**
 * 
 * @export
 * @interface GetOffererNameResponseModel
 */
export interface GetOffererNameResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererNameResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOffererNameResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetOffererNameResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetOffererResponseModel
 */
export interface GetOffererResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {OffererApiKey}
   * @memberof GetOffererResponseModel
   */
  apiKey: OffererApiKey
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasActiveOffer: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasAvailablePricingPoints: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasBankAccountWithPendingCorrections: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasDigitalVenueAtLeastOneOffer: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasNonFreeOffer: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasPendingBankAccount: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  hasValidBankAccount: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  isOnboarded: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererResponseModel
   */
  isValidated: boolean
  /**
   * 
   * @type {Array<GetOffererVenueResponseModel>}
   * @memberof GetOffererResponseModel
   */
  managedVenues?: Array<GetOffererVenueResponseModel>
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  siren?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererResponseModel
   */
  street?: string
  /**
   * 
   * @type {Array<number>}
   * @memberof GetOffererResponseModel
   */
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>
}
/**
 * 
 * @export
 * @interface GetOffererStatsResponseModel
 */
export interface GetOffererStatsResponseModel {
  /**
   * 
   * @type {OffererStatsDataModel}
   * @memberof GetOffererStatsResponseModel
   */
  jsonData: OffererStatsDataModel
  /**
   * 
   * @type {number}
   * @memberof GetOffererStatsResponseModel
   */
  offererId: number
  /**
   * 
   * @type {string}
   * @memberof GetOffererStatsResponseModel
   */
  syncDate?: string
}
/**
 * 
 * @export
 * @interface GetOffererV2StatsResponseModel
 */
export interface GetOffererV2StatsResponseModel {
  /**
   * 
   * @type {number}
   * @memberof GetOffererV2StatsResponseModel
   */
  pendingEducationalOffers: number
  /**
   * 
   * @type {number}
   * @memberof GetOffererV2StatsResponseModel
   */
  pendingPublicOffers: number
  /**
   * 
   * @type {number}
   * @memberof GetOffererV2StatsResponseModel
   */
  publishedEducationalOffers: number
  /**
   * 
   * @type {number}
   * @memberof GetOffererV2StatsResponseModel
   */
  publishedPublicOffers: number
}
/**
 * 
 * @export
 * @interface GetOffererVenueResponseModel
 */
export interface GetOffererVenueResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  adageInscriptionDate?: string
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {BannerMetaModel}
   * @memberof GetOffererVenueResponseModel
   */
  bannerMeta?: BannerMetaModel
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  bannerUrl?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  city?: string
  /**
   * 
   * @type {Array<DMSApplicationForEAC>}
   * @memberof GetOffererVenueResponseModel
   */
  collectiveDmsApplications: Array<DMSApplicationForEAC>
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  comment?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  hasAdageId: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  hasCreatedOffer: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  hasVenueProviders: boolean
  /**
   * 
   * @type {number}
   * @memberof GetOffererVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  isPermanent: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  isVisibleInApp?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  siret?: string
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  street?: string
  /**
   * 
   * @type {VenueTypeCode}
   * @memberof GetOffererVenueResponseModel
   */
  venueTypeCode: VenueTypeCode
  /**
   * 
   * @type {boolean}
   * @memberof GetOffererVenueResponseModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetOffererVenueResponseModel
   */
  withdrawalDetails?: string
}
/**
 * 
 * @export
 * @interface GetOfferersNamesQueryModel
 */
export interface GetOfferersNamesQueryModel {
  /**
   * 
   * @type {number}
   * @memberof GetOfferersNamesQueryModel
   */
  offerer_id?: number
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferersNamesQueryModel
   */
  validated?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetOfferersNamesQueryModel
   */
  validated_for_user?: boolean
}
/**
 * 
 * @export
 * @interface GetOfferersNamesResponseModel
 */
export interface GetOfferersNamesResponseModel {
  /**
   * 
   * @type {Array<GetOffererNameResponseModel>}
   * @memberof GetOfferersNamesResponseModel
   */
  offerersNames: Array<GetOffererNameResponseModel>
}
/**
 * 
 * @export
 * @interface GetProductInformations
 */
export interface GetProductInformations {
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  author: string
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  description?: string
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  gtlId: string
  /**
   * 
   * @type {number}
   * @memberof GetProductInformations
   */
  id: number
  /**
   * 
   * @type {any}
   * @memberof GetProductInformations
   */
  images: any
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  performer: string
  /**
   * 
   * @type {string}
   * @memberof GetProductInformations
   */
  subcategoryId: string
}
/**
 * 
 * @export
 * @interface GetStocksResponseModel
 */
export interface GetStocksResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetStocksResponseModel
   */
  hasStocks: boolean
  /**
   * 
   * @type {number}
   * @memberof GetStocksResponseModel
   */
  stockCount: number
  /**
   * 
   * @type {Array<GetOfferStockResponseModel>}
   * @memberof GetStocksResponseModel
   */
  stocks: Array<GetOfferStockResponseModel>
}
/**
 * 
 * @export
 * @interface GetVenueDomainResponseModel
 */
export interface GetVenueDomainResponseModel {
  /**
   * 
   * @type {number}
   * @memberof GetVenueDomainResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetVenueDomainResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface GetVenueListResponseModel
 */
export interface GetVenueListResponseModel {
  /**
   * 
   * @type {Array<VenueListItemResponseModel>}
   * @memberof GetVenueListResponseModel
   */
  venues: Array<VenueListItemResponseModel>
}
/**
 * 
 * @export
 * @interface GetVenueManagingOffererResponseModel
 */
export interface GetVenueManagingOffererResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueManagingOffererResponseModel
   */
  allowedOnAdage: boolean
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {number}
   * @memberof GetVenueManagingOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueManagingOffererResponseModel
   */
  isValidated: boolean
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  siren?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueManagingOffererResponseModel
   */
  street?: string
}
/**
 * 
 * @export
 * @interface GetVenuePricingPointResponseModel
 */
export interface GetVenuePricingPointResponseModel {
  /**
   * 
   * @type {number}
   * @memberof GetVenuePricingPointResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof GetVenuePricingPointResponseModel
   */
  siret: string
  /**
   * 
   * @type {string}
   * @memberof GetVenuePricingPointResponseModel
   */
  venueName: string
}
/**
 * 
 * @export
 * @interface GetVenueResponseModel
 */
export interface GetVenueResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  adageInscriptionDate?: string
  /**
   * 
   * @type {AddressResponseIsLinkedToVenueModel}
   * @memberof GetVenueResponseModel
   */
  address?: AddressResponseIsLinkedToVenueModel
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  banId?: string
  /**
   * 
   * @type {BankAccountResponseModel}
   * @memberof GetVenueResponseModel
   */
  bankAccount?: BankAccountResponseModel
  /**
   * 
   * @type {BannerMetaModel}
   * @memberof GetVenueResponseModel
   */
  bannerMeta?: BannerMetaModel
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  bannerUrl?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  city?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectiveAccessInformation?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectiveDescription?: string
  /**
   * 
   * @type {Array<DMSApplicationForEAC>}
   * @memberof GetVenueResponseModel
   */
  collectiveDmsApplications: Array<DMSApplicationForEAC>
  /**
   * 
   * @type {Array<GetVenueDomainResponseModel>}
   * @memberof GetVenueResponseModel
   */
  collectiveDomains: Array<GetVenueDomainResponseModel>
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectiveEmail?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof GetVenueResponseModel
   */
  collectiveInterventionArea?: Array<string>
  /**
   * 
   * @type {LegalStatusResponseModel}
   * @memberof GetVenueResponseModel
   */
  collectiveLegalStatus?: LegalStatusResponseModel
  /**
   * 
   * @type {Array<string>}
   * @memberof GetVenueResponseModel
   */
  collectiveNetwork?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectivePhone?: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof GetVenueResponseModel
   */
  collectiveStudents?: Array<StudentLevels>
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectiveSubCategoryId?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  collectiveWebsite?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  comment?: string
  /**
   * 
   * @type {VenueContactModel}
   * @memberof GetVenueResponseModel
   */
  contact?: VenueContactModel
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  description?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  dmsToken: string
  /**
   * 
   * @type {ExternalAccessibilityDataModel}
   * @memberof GetVenueResponseModel
   */
  externalAccessibilityData?: ExternalAccessibilityDataModel
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  externalAccessibilityId?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  externalAccessibilityUrl?: string
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  hasAdageId: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  hasOffers: boolean
  /**
   * 
   * @type {number}
   * @memberof GetVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  isPermanent?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  isVisibleInApp?: boolean
  /**
   * 
   * @type {number}
   * @memberof GetVenueResponseModel
   */
  latitude?: number
  /**
   * 
   * @type {number}
   * @memberof GetVenueResponseModel
   */
  longitude?: number
  /**
   * 
   * @type {GetVenueManagingOffererResponseModel}
   * @memberof GetVenueResponseModel
   */
  managingOfferer: GetVenueManagingOffererResponseModel
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {any}
   * @memberof GetVenueResponseModel
   */
  openingHours?: any
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {GetVenuePricingPointResponseModel}
   * @memberof GetVenueResponseModel
   */
  pricingPoint?: GetVenuePricingPointResponseModel
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  siret?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  street?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  timezone: string
  /**
   * 
   * @type {number}
   * @memberof GetVenueResponseModel
   */
  venueLabelId?: number
  /**
   * 
   * @type {VenueTypeCode}
   * @memberof GetVenueResponseModel
   */
  venueTypeCode: VenueTypeCode
  /**
   * 
   * @type {boolean}
   * @memberof GetVenueResponseModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof GetVenueResponseModel
   */
  withdrawalDetails?: string
}
/**
 * 
 * @export
 * @interface GetVenuesOfOffererFromSiretResponseModel
 */
export interface GetVenuesOfOffererFromSiretResponseModel {
  /**
   * 
   * @type {string}
   * @memberof GetVenuesOfOffererFromSiretResponseModel
   */
  offererName?: string
  /**
   * 
   * @type {string}
   * @memberof GetVenuesOfOffererFromSiretResponseModel
   */
  offererSiren?: string
  /**
   * 
   * @type {Array<VenueOfOffererFromSiretResponseModel>}
   * @memberof GetVenuesOfOffererFromSiretResponseModel
   */
  venues: Array<VenueOfOffererFromSiretResponseModel>
}
/**
 * 
 * @export
 * @interface HasInvoiceQueryModel
 */
export interface HasInvoiceQueryModel {
  /**
   * 
   * @type {number}
   * @memberof HasInvoiceQueryModel
   */
  offererId: number
}
/**
 * 
 * @export
 * @interface HasInvoiceResponseModel
 */
export interface HasInvoiceResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof HasInvoiceResponseModel
   */
  hasInvoice: boolean
}
/**
 * 
 * @export
 * @interface IndividualRevenue
 */
export interface IndividualRevenue {
  /**
   * 
   * @type {number}
   * @memberof IndividualRevenue
   */
  individual: number
}
/**
 * 
 * @export
 * @interface InviteMemberQueryModel
 */
export interface InviteMemberQueryModel {
  /**
   * 
   * @type {string}
   * @memberof InviteMemberQueryModel
   */
  email: string
}
/**
 * 
 * @export
 * @interface InvoiceListV2QueryModel
 */
export interface InvoiceListV2QueryModel {
  /**
   * 
   * @type {number}
   * @memberof InvoiceListV2QueryModel
   */
  bankAccountId?: number
  /**
   * 
   * @type {number}
   * @memberof InvoiceListV2QueryModel
   */
  offererId?: number
  /**
   * 
   * @type {string}
   * @memberof InvoiceListV2QueryModel
   */
  periodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof InvoiceListV2QueryModel
   */
  periodEndingDate?: string
}
/**
 * 
 * @export
 */
export type InvoiceListV2ResponseModel = Array<InvoiceResponseV2Model>
/**
 * 
 * @export
 * @interface InvoiceResponseV2Model
 */
export interface InvoiceResponseV2Model {
  /**
   * 
   * @type {number}
   * @memberof InvoiceResponseV2Model
   */
  amount: number
  /**
   * 
   * @type {string}
   * @memberof InvoiceResponseV2Model
   */
  bankAccountLabel?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof InvoiceResponseV2Model
   */
  cashflowLabels: Array<string>
  /**
   * 
   * @type {string}
   * @memberof InvoiceResponseV2Model
   */
  date: string
  /**
   * 
   * @type {string}
   * @memberof InvoiceResponseV2Model
   */
  reference: string
  /**
   * 
   * @type {string}
   * @memberof InvoiceResponseV2Model
   */
  url: string
}
/**
 * 
 * @export
 * @interface LegalStatusResponseModel
 */
export interface LegalStatusResponseModel {
  /**
   * 
   * @type {number}
   * @memberof LegalStatusResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof LegalStatusResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface LinkVenueToBankAccountBodyModel
 */
export interface LinkVenueToBankAccountBodyModel {
  /**
   * 
   * @type {Array<number>}
   * @memberof LinkVenueToBankAccountBodyModel
   */
  venues_ids: Array<number>
}
/**
 * 
 * @export
 * @interface LinkVenueToPricingPointBodyModel
 */
export interface LinkVenueToPricingPointBodyModel {
  /**
   * 
   * @type {number}
   * @memberof LinkVenueToPricingPointBodyModel
   */
  pricingPointId: number
}
/**
 * A venue that is already linked to a bank account.
 * @export
 * @interface LinkedVenues
 */
export interface LinkedVenues {
  /**
   * 
   * @type {string}
   * @memberof LinkedVenues
   */
  commonName: string
  /**
   * 
   * @type {number}
   * @memberof LinkedVenues
   */
  id: number
}
/**
 * 
 * @export
 * @interface ListBookingsQueryModel
 */
export interface ListBookingsQueryModel {
  /**
   * 
   * @type {string}
   * @memberof ListBookingsQueryModel
   */
  bookingPeriodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof ListBookingsQueryModel
   */
  bookingPeriodEndingDate?: string
  /**
   * 
   * @type {BookingStatusFilter}
   * @memberof ListBookingsQueryModel
   */
  bookingStatusFilter?: BookingStatusFilter
  /**
   * 
   * @type {string}
   * @memberof ListBookingsQueryModel
   */
  eventDate?: string
  /**
   * 
   * @type {BookingExportType}
   * @memberof ListBookingsQueryModel
   */
  exportType?: BookingExportType
  /**
   * 
   * @type {number}
   * @memberof ListBookingsQueryModel
   */
  offerId?: number
  /**
   * 
   * @type {number}
   * @memberof ListBookingsQueryModel
   */
  offererAddressId?: number
  /**
   * 
   * @type {number}
   * @memberof ListBookingsQueryModel
   */
  page?: number
  /**
   * 
   * @type {number}
   * @memberof ListBookingsQueryModel
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface ListBookingsResponseModel
 */
export interface ListBookingsResponseModel {
  /**
   * 
   * @type {Array<BookingRecapResponseModel>}
   * @memberof ListBookingsResponseModel
   */
  bookingsRecap: Array<BookingRecapResponseModel>
  /**
   * 
   * @type {number}
   * @memberof ListBookingsResponseModel
   */
  page: number
  /**
   * 
   * @type {number}
   * @memberof ListBookingsResponseModel
   */
  pages: number
  /**
   * 
   * @type {number}
   * @memberof ListBookingsResponseModel
   */
  total: number
}
/**
 * 
 * @export
 * @interface ListCollectiveBookingsQueryModel
 */
export interface ListCollectiveBookingsQueryModel {
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveBookingsQueryModel
   */
  bookingPeriodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveBookingsQueryModel
   */
  bookingPeriodEndingDate?: string
  /**
   * 
   * @type {CollectiveBookingStatusFilter}
   * @memberof ListCollectiveBookingsQueryModel
   */
  bookingStatusFilter?: CollectiveBookingStatusFilter
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveBookingsQueryModel
   */
  eventDate?: string
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveBookingsQueryModel
   */
  page?: number
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveBookingsQueryModel
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface ListCollectiveBookingsResponseModel
 */
export interface ListCollectiveBookingsResponseModel {
  /**
   * 
   * @type {Array<CollectiveBookingResponseModel>}
   * @memberof ListCollectiveBookingsResponseModel
   */
  bookingsRecap: Array<CollectiveBookingResponseModel>
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveBookingsResponseModel
   */
  page: number
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveBookingsResponseModel
   */
  pages: number
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveBookingsResponseModel
   */
  total: number
}
/**
 * 
 * @export
 * @interface ListCollectiveOffersQueryModel
 */
export interface ListCollectiveOffersQueryModel {
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveOffersQueryModel
   */
  categoryId?: string
  /**
   * 
   * @type {CollectiveOfferType}
   * @memberof ListCollectiveOffersQueryModel
   */
  collectiveOfferType?: CollectiveOfferType
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveOffersQueryModel
   */
  creationMode?: string
  /**
   * 
   * @type {EacFormat}
   * @memberof ListCollectiveOffersQueryModel
   */
  format?: EacFormat
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveOffersQueryModel
   */
  nameOrIsbn?: string
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveOffersQueryModel
   */
  offererId?: number
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveOffersQueryModel
   */
  periodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof ListCollectiveOffersQueryModel
   */
  periodEndingDate?: string
  /**
   * 
   * @type {Array<CollectiveOfferDisplayedStatus> | CollectiveOfferDisplayedStatus}
   * @memberof ListCollectiveOffersQueryModel
   */
  status?: Array<CollectiveOfferDisplayedStatus> | CollectiveOfferDisplayedStatus
  /**
   * 
   * @type {number}
   * @memberof ListCollectiveOffersQueryModel
   */
  venueId?: number
}
/**
 * 
 * @export
 */
export type ListCollectiveOffersResponseModel = Array<CollectiveOfferResponseModel>
/**
 * 
 * @export
 */
export type ListFeatureResponseModel = Array<FeatureResponseModel>
/**
 * 
 * @export
 */
export type ListNationalProgramsResponseModel = Array<NationalProgramModel>
/**
 * 
 * @export
 * @interface ListOffersOfferResponseModel
 */
export interface ListOffersOfferResponseModel {
  /**
   * 
   * @type {AddressResponseIsLinkedToVenueModel}
   * @memberof ListOffersOfferResponseModel
   */
  address?: AddressResponseIsLinkedToVenueModel
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  hasBookingLimitDatetimesPassed: boolean
  /**
   * 
   * @type {number}
   * @memberof ListOffersOfferResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isEditable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isEducational: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isEvent: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isShowcase?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersOfferResponseModel
   */
  isThing: boolean
  /**
   * 
   * @type {string}
   * @memberof ListOffersOfferResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof ListOffersOfferResponseModel
   */
  productIsbn?: string
  /**
   * 
   * @type {OfferStatus}
   * @memberof ListOffersOfferResponseModel
   */
  status: OfferStatus
  /**
   * 
   * @type {Array<ListOffersStockResponseModel>}
   * @memberof ListOffersOfferResponseModel
   */
  stocks: Array<ListOffersStockResponseModel>
  /**
   * 
   * @type {SubcategoryIdEnum}
   * @memberof ListOffersOfferResponseModel
   */
  subcategoryId: SubcategoryIdEnum
  /**
   * 
   * @type {string}
   * @memberof ListOffersOfferResponseModel
   */
  thumbUrl?: string
  /**
   * 
   * @type {ListOffersVenueResponseModel}
   * @memberof ListOffersOfferResponseModel
   */
  venue: ListOffersVenueResponseModel
}
/**
 * 
 * @export
 * @interface ListOffersQueryModel
 */
export interface ListOffersQueryModel {
  /**
   * 
   * @type {string}
   * @memberof ListOffersQueryModel
   */
  categoryId?: string
  /**
   * 
   * @type {CollectiveOfferType}
   * @memberof ListOffersQueryModel
   */
  collectiveOfferType?: CollectiveOfferType
  /**
   * 
   * @type {string}
   * @memberof ListOffersQueryModel
   */
  creationMode?: string
  /**
   * 
   * @type {string}
   * @memberof ListOffersQueryModel
   */
  nameOrIsbn?: string
  /**
   * 
   * @type {number}
   * @memberof ListOffersQueryModel
   */
  offererAddressId?: number
  /**
   * 
   * @type {number}
   * @memberof ListOffersQueryModel
   */
  offererId?: number
  /**
   * 
   * @type {string}
   * @memberof ListOffersQueryModel
   */
  periodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof ListOffersQueryModel
   */
  periodEndingDate?: string
  /**
   * 
   * @type {OfferStatus | CollectiveOfferDisplayedStatus}
   * @memberof ListOffersQueryModel
   */
  status?: OfferStatus | CollectiveOfferDisplayedStatus
  /**
   * 
   * @type {number}
   * @memberof ListOffersQueryModel
   */
  venueId?: number
}
/**
 * 
 * @export
 */
export type ListOffersResponseModel = Array<ListOffersOfferResponseModel>
/**
 * 
 * @export
 * @interface ListOffersStockResponseModel
 */
export interface ListOffersStockResponseModel {
  /**
   * 
   * @type {string}
   * @memberof ListOffersStockResponseModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof ListOffersStockResponseModel
   */
  bookingQuantity?: number
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersStockResponseModel
   */
  hasBookingLimitDatetimePassed: boolean
  /**
   * 
   * @type {number}
   * @memberof ListOffersStockResponseModel
   */
  id: number
  /**
   * 
   * @type {number | string}
   * @memberof ListOffersStockResponseModel
   */
  remainingQuantity: number | string
}
/**
 * 
 * @export
 * @interface ListOffersVenueResponseModel
 */
export interface ListOffersVenueResponseModel {
  /**
   * 
   * @type {string}
   * @memberof ListOffersVenueResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {number}
   * @memberof ListOffersVenueResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof ListOffersVenueResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {string}
   * @memberof ListOffersVenueResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof ListOffersVenueResponseModel
   */
  offererName: string
  /**
   * 
   * @type {string}
   * @memberof ListOffersVenueResponseModel
   */
  publicName?: string
}
/**
 * 
 * @export
 */
export type ListProviderResponse = Array<ProviderResponse>
/**
 * 
 * @export
 * @interface ListVenueProviderQuery
 */
export interface ListVenueProviderQuery {
  /**
   * 
   * @type {number}
   * @memberof ListVenueProviderQuery
   */
  venueId: number
}
/**
 * 
 * @export
 * @interface ListVenueProviderResponse
 */
export interface ListVenueProviderResponse {
  /**
   * 
   * @type {Array<VenueProviderResponse>}
   * @memberof ListVenueProviderResponse
   */
  venue_providers: Array<VenueProviderResponse>
}
/**
 * 
 * @export
 * @interface LoginUserBodyModel
 */
export interface LoginUserBodyModel {
  /**
   * 
   * @type {string}
   * @memberof LoginUserBodyModel
   */
  captchaToken?: string
  /**
   * 
   * @type {string}
   * @memberof LoginUserBodyModel
   */
  identifier: string
  /**
   * 
   * @type {string}
   * @memberof LoginUserBodyModel
   */
  password: string
}
/**
 * 
 * @export
 * @interface ManagedVenues
 */
export interface ManagedVenues {
  /**
   * 
   * @type {number}
   * @memberof ManagedVenues
   */
  bankAccountId?: number
  /**
   * 
   * @type {string}
   * @memberof ManagedVenues
   */
  commonName: string
  /**
   * 
   * @type {boolean}
   * @memberof ManagedVenues
   */
  hasPricingPoint: boolean
  /**
   * 
   * @type {number}
   * @memberof ManagedVenues
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof ManagedVenues
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof ManagedVenues
   */
  siret?: string
}
/**
 * 
 * @export
 * @interface MentalDisabilityModel
 */
export interface MentalDisabilityModel {
  /**
   * 
   * @type {string}
   * @memberof MentalDisabilityModel
   */
  trainedPersonnel?: string
}
/**
 * 
 * @export
 * @interface MotorDisabilityModel
 */
export interface MotorDisabilityModel {
  /**
   * 
   * @type {string}
   * @memberof MotorDisabilityModel
   */
  entrance?: string
  /**
   * 
   * @type {string}
   * @memberof MotorDisabilityModel
   */
  exterior?: string
  /**
   * 
   * @type {string}
   * @memberof MotorDisabilityModel
   */
  facilities?: string
  /**
   * 
   * @type {string}
   * @memberof MotorDisabilityModel
   */
  parking?: string
}
/**
 * 
 * @export
 * @interface MusicTypeResponse
 */
export interface MusicTypeResponse {
  /**
   * 
   * @type {boolean}
   * @memberof MusicTypeResponse
   */
  canBeEvent: boolean
  /**
   * 
   * @type {string}
   * @memberof MusicTypeResponse
   */
  gtl_id: string
  /**
   * 
   * @type {string}
   * @memberof MusicTypeResponse
   */
  label: string
}
/**
 * 
 * @export
 * @interface NationalProgramModel
 */
export interface NationalProgramModel {
  /**
   * National program id
   * @type {number}
   * @memberof NationalProgramModel
   */
  id: number
  /**
   * National program name
   * @type {string}
   * @memberof NationalProgramModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface NewPasswordBodyModel
 */
export interface NewPasswordBodyModel {
  /**
   * 
   * @type {string}
   * @memberof NewPasswordBodyModel
   */
  newPassword: string
  /**
   * 
   * @type {string}
   * @memberof NewPasswordBodyModel
   */
  token: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum OfferAddressType {
  OffererVenue = <any> 'offererVenue',
  School = <any> 'school',
  Other = <any> 'other'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum OfferContactFormEnum {
  Form = <any> 'form'
}
/**
 * 
 * @export
 * @interface OfferDomain
 */
export interface OfferDomain {
  /**
   * 
   * @type {number}
   * @memberof OfferDomain
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof OfferDomain
   */
  name: string
}
/**
 * 
 * @export
 * @interface OfferImage
 */
export interface OfferImage {
  /**
   * 
   * @type {string}
   * @memberof OfferImage
   */
  credit?: string
  /**
   * 
   * @type {string}
   * @memberof OfferImage
   */
  url: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum OfferStatus {
  ACTIVE = <any> 'ACTIVE',
  PENDING = <any> 'PENDING',
  EXPIRED = <any> 'EXPIRED',
  REJECTED = <any> 'REJECTED',
  SOLDOUT = <any> 'SOLD_OUT',
  INACTIVE = <any> 'INACTIVE',
  DRAFT = <any> 'DRAFT'
}
/**
 * 
 * @export
 * @interface OffererAddressRequestModel
 */
export interface OffererAddressRequestModel {
  /**
   * 
   * @type {string}
   * @memberof OffererAddressRequestModel
   */
  inseeCode: string
  /**
   * 
   * @type {string}
   * @memberof OffererAddressRequestModel
   */
  label?: string
  /**
   * 
   * @type {string}
   * @memberof OffererAddressRequestModel
   */
  street: string
}
/**
 * 
 * @export
 * @interface OffererAddressResponseModel
 */
export interface OffererAddressResponseModel {
  /**
   * 
   * @type {AddressResponseModel}
   * @memberof OffererAddressResponseModel
   */
  address: AddressResponseModel
  /**
   * 
   * @type {number}
   * @memberof OffererAddressResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof OffererAddressResponseModel
   */
  label?: string
  /**
   * 
   * @type {number}
   * @memberof OffererAddressResponseModel
   */
  offererId: number
}
/**
 * 
 * @export
 * @interface OffererApiKey
 */
export interface OffererApiKey {
  /**
   * 
   * @type {number}
   * @memberof OffererApiKey
   */
  maxAllowed: number
  /**
   * 
   * @type {Array<string>}
   * @memberof OffererApiKey
   */
  prefixes: Array<string>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum OffererMemberStatus {
  Validated = <any> 'validated',
  Pending = <any> 'pending'
}
/**
 * 
 * @export
 * @interface OffererStatsDataModel
 */
export interface OffererStatsDataModel {
  /**
   * 
   * @type {Array<OffererViewsModel>}
   * @memberof OffererStatsDataModel
   */
  dailyViews: Array<OffererViewsModel>
  /**
   * 
   * @type {Array<TopOffersResponseData>}
   * @memberof OffererStatsDataModel
   */
  topOffers: Array<TopOffersResponseData>
  /**
   * 
   * @type {number}
   * @memberof OffererStatsDataModel
   */
  totalViewsLast30Days: number
}
/**
 * 
 * @export
 * @interface OffererStatsResponseModel
 */
export interface OffererStatsResponseModel {
  /**
   * 
   * @type {string}
   * @memberof OffererStatsResponseModel
   */
  dashboardUrl: string
}
/**
 * 
 * @export
 * @interface OffererViewsModel
 */
export interface OffererViewsModel {
  /**
   * 
   * @type {string}
   * @memberof OffererViewsModel
   */
  eventDate: string
  /**
   * 
   * @type {number}
   * @memberof OffererViewsModel
   */
  numberOfViews: number
}
/**
 * 
 * @export
 * @interface OpeningHoursModel
 */
export interface OpeningHoursModel {
  /**
   * 
   * @type {Array<Array<string>>}
   * @memberof OpeningHoursModel
   */
  timespan?: Array<Array<string>>
  /**
   * 
   * @type {string}
   * @memberof OpeningHoursModel
   */
  weekday: string
}
/**
 * 
 * @export
 * @interface OrderBy
 */
export interface OrderBy extends StocksOrderedBy {
}
/**
 * 
 * @export
 * @interface PatchAllOffersActiveStatusBodyModel
 */
export interface PatchAllOffersActiveStatusBodyModel {
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  categoryId?: string
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  creationMode?: string
  /**
   * 
   * @type {boolean}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  isActive: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  nameOrIsbn?: string
  /**
   * 
   * @type {number}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  offererId?: number
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  periodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  periodEndingDate?: string
  /**
   * 
   * @type {string}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  status?: string
  /**
   * 
   * @type {number}
   * @memberof PatchAllOffersActiveStatusBodyModel
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface PatchCollectiveOfferActiveStatusBodyModel
 */
export interface PatchCollectiveOfferActiveStatusBodyModel {
  /**
   * 
   * @type {Array<number>}
   * @memberof PatchCollectiveOfferActiveStatusBodyModel
   */
  ids: Array<number>
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferActiveStatusBodyModel
   */
  isActive: boolean
}
/**
 * 
 * @export
 * @interface PatchCollectiveOfferArchiveBodyModel
 */
export interface PatchCollectiveOfferArchiveBodyModel {
  /**
   * 
   * @type {Array<number>}
   * @memberof PatchCollectiveOfferArchiveBodyModel
   */
  ids: Array<number>
}
/**
 * 
 * @export
 * @interface PatchCollectiveOfferBodyModel
 */
export interface PatchCollectiveOfferBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof PatchCollectiveOfferBodyModel
   */
  bookingEmails?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferBodyModel
   */
  contactEmail?: string
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferBodyModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferBodyModel
   */
  description?: string
  /**
   * 
   * @type {Array<number>}
   * @memberof PatchCollectiveOfferBodyModel
   */
  domains?: Array<number>
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof PatchCollectiveOfferBodyModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {Array<string>}
   * @memberof PatchCollectiveOfferBodyModel
   */
  interventionArea?: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferBodyModel
   */
  name?: string
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferBodyModel
   */
  nationalProgramId?: number
  /**
   * 
   * @type {CollectiveOfferVenueBodyModel}
   * @memberof PatchCollectiveOfferBodyModel
   */
  offerVenue?: CollectiveOfferVenueBodyModel
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof PatchCollectiveOfferBodyModel
   */
  students?: Array<StudentLevels>
  /**
   * 
   * @type {SubcategoryIdEnum | string}
   * @memberof PatchCollectiveOfferBodyModel
   */
  subcategoryId?: SubcategoryIdEnum | string
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferBodyModel
   */
  venueId?: number
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferBodyModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface PatchCollectiveOfferEducationalInstitution
 */
export interface PatchCollectiveOfferEducationalInstitution {
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferEducationalInstitution
   */
  educationalInstitutionId?: number
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferEducationalInstitution
   */
  teacherEmail?: string
}
/**
 * 
 * @export
 * @interface PatchCollectiveOfferTemplateBodyModel
 */
export interface PatchCollectiveOfferTemplateBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  bookingEmails?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  contactEmail?: string
  /**
   * 
   * @type {OfferContactFormEnum}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  contactForm?: OfferContactFormEnum
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  contactUrl?: string
  /**
   * 
   * @type {DateRangeModel}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  dates?: DateRangeModel
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  description?: string
  /**
   * 
   * @type {Array<number>}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  domains?: Array<number>
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {Array<string>}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  interventionArea?: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  name?: string
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  nationalProgramId?: number
  /**
   * 
   * @type {CollectiveOfferVenueBodyModel}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  offerVenue?: CollectiveOfferVenueBodyModel
  /**
   * 
   * @type {string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  priceDetail?: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  students?: Array<StudentLevels>
  /**
   * 
   * @type {SubcategoryIdEnum | string}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  subcategoryId?: SubcategoryIdEnum | string
  /**
   * 
   * @type {number}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  venueId?: number
  /**
   * 
   * @type {boolean}
   * @memberof PatchCollectiveOfferTemplateBodyModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface PatchDraftOfferBodyModel
 */
export interface PatchDraftOfferBodyModel {
  /**
   * 
   * @type {string}
   * @memberof PatchDraftOfferBodyModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof PatchDraftOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {any}
   * @memberof PatchDraftOfferBodyModel
   */
  extraData?: any
  /**
   * 
   * @type {string}
   * @memberof PatchDraftOfferBodyModel
   */
  name?: string
  /**
   * 
   * @type {string}
   * @memberof PatchDraftOfferBodyModel
   */
  subcategoryId?: string
}
/**
 * 
 * @export
 * @interface PatchOfferActiveStatusBodyModel
 */
export interface PatchOfferActiveStatusBodyModel {
  /**
   * 
   * @type {Array<number>}
   * @memberof PatchOfferActiveStatusBodyModel
   */
  ids: Array<number>
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferActiveStatusBodyModel
   */
  isActive: boolean
}
/**
 * 
 * @export
 * @interface PatchOfferBodyModel
 */
export interface PatchOfferBodyModel {
  /**
   * 
   * @type {AddressBodyModel}
   * @memberof PatchOfferBodyModel
   */
  address?: AddressBodyModel
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  bookingContact?: string
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof PatchOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  externalTicketOfficeUrl?: string
  /**
   * 
   * @type {any}
   * @memberof PatchOfferBodyModel
   */
  extraData?: any
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  isActive?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  isDuo?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  isNational?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  name?: string
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  shouldSendMail?: boolean
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  url?: string
  /**
   * 
   * @type {boolean}
   * @memberof PatchOfferBodyModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {number}
   * @memberof PatchOfferBodyModel
   */
  withdrawalDelay?: number
  /**
   * 
   * @type {string}
   * @memberof PatchOfferBodyModel
   */
  withdrawalDetails?: string
  /**
   * 
   * @type {WithdrawalTypeEnum}
   * @memberof PatchOfferBodyModel
   */
  withdrawalType?: WithdrawalTypeEnum
}
/**
 * 
 * @export
 * @interface PatchOfferPublishBodyModel
 */
export interface PatchOfferPublishBodyModel {
  /**
   * 
   * @type {number}
   * @memberof PatchOfferPublishBodyModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof PatchOfferPublishBodyModel
   */
  publicationDate?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum PhoneValidationStatusType {
  SkippedBySupport = <any> 'skipped-by-support',
  Unvalidated = <any> 'unvalidated',
  Validated = <any> 'validated'
}
/**
 * 
 * @export
 * @interface PostCollectiveOfferBodyModel
 */
export interface PostCollectiveOfferBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof PostCollectiveOfferBodyModel
   */
  bookingEmails: Array<string>
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  contactEmail?: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  description: string
  /**
   * 
   * @type {Array<number>}
   * @memberof PostCollectiveOfferBodyModel
   */
  domains?: Array<number>
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof PostCollectiveOfferBodyModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {Array<string>}
   * @memberof PostCollectiveOfferBodyModel
   */
  interventionArea?: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  name: string
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferBodyModel
   */
  nationalProgramId?: number
  /**
   * 
   * @type {CollectiveOfferVenueBodyModel}
   * @memberof PostCollectiveOfferBodyModel
   */
  offerVenue: CollectiveOfferVenueBodyModel
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  offererId?: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof PostCollectiveOfferBodyModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferBodyModel
   */
  subcategoryId?: string
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferBodyModel
   */
  templateId?: number
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferBodyModel
   */
  venueId: number
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferBodyModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface PostCollectiveOfferTemplateBodyModel
 */
export interface PostCollectiveOfferTemplateBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {Array<string>}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  bookingEmails: Array<string>
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  contactEmail?: string
  /**
   * 
   * @type {OfferContactFormEnum}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  contactForm?: OfferContactFormEnum
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  contactUrl?: string
  /**
   * 
   * @type {DateRangeOnCreateModel}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  dates?: DateRangeOnCreateModel
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  description: string
  /**
   * 
   * @type {Array<number>}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  domains?: Array<number>
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {Array<string>}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  interventionArea?: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  name: string
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  nationalProgramId?: number
  /**
   * 
   * @type {CollectiveOfferVenueBodyModel}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  offerVenue: CollectiveOfferVenueBodyModel
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  offererId?: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  priceDetail?: string
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  subcategoryId?: string
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  templateId?: number
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  venueId: number
  /**
   * 
   * @type {boolean}
   * @memberof PostCollectiveOfferTemplateBodyModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface PostDraftOfferBodyModel
 */
export interface PostDraftOfferBodyModel {
  /**
   * 
   * @type {string}
   * @memberof PostDraftOfferBodyModel
   */
  callId?: string
  /**
   * 
   * @type {string}
   * @memberof PostDraftOfferBodyModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof PostDraftOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {any}
   * @memberof PostDraftOfferBodyModel
   */
  extraData?: any
  /**
   * 
   * @type {string}
   * @memberof PostDraftOfferBodyModel
   */
  name: string
  /**
   * 
   * @type {number}
   * @memberof PostDraftOfferBodyModel
   */
  productId?: number
  /**
   * 
   * @type {string}
   * @memberof PostDraftOfferBodyModel
   */
  subcategoryId: string
  /**
   * 
   * @type {number}
   * @memberof PostDraftOfferBodyModel
   */
  venueId: number
}
/**
 * 
 * @export
 * @interface PostOfferBodyModel
 */
export interface PostOfferBodyModel {
  /**
   * 
   * @type {AddressBodyModel}
   * @memberof PostOfferBodyModel
   */
  address?: AddressBodyModel
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  audioDisabilityCompliant: boolean
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  bookingContact?: string
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof PostOfferBodyModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  externalTicketOfficeUrl?: string
  /**
   * 
   * @type {any}
   * @memberof PostOfferBodyModel
   */
  extraData?: any
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  isDuo?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  isNational?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  mentalDisabilityCompliant: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  motorDisabilityCompliant: boolean
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  subcategoryId: string
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  url?: string
  /**
   * 
   * @type {number}
   * @memberof PostOfferBodyModel
   */
  venueId: number
  /**
   * 
   * @type {boolean}
   * @memberof PostOfferBodyModel
   */
  visualDisabilityCompliant: boolean
  /**
   * 
   * @type {number}
   * @memberof PostOfferBodyModel
   */
  withdrawalDelay?: number
  /**
   * 
   * @type {string}
   * @memberof PostOfferBodyModel
   */
  withdrawalDetails?: string
  /**
   * 
   * @type {WithdrawalTypeEnum}
   * @memberof PostOfferBodyModel
   */
  withdrawalType?: WithdrawalTypeEnum
}
/**
 * 
 * @export
 * @interface PostOffererResponseModel
 */
export interface PostOffererResponseModel {
  /**
   * 
   * @type {number}
   * @memberof PostOffererResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof PostOffererResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof PostOffererResponseModel
   */
  siren: string
}
/**
 * 
 * @export
 * @interface PostVenueBodyModel
 */
export interface PostVenueBodyModel {
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueBodyModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  banId?: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  bookingEmail: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  city: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  comment?: string
  /**
   * 
   * @type {VenueContactModel}
   * @memberof PostVenueBodyModel
   */
  contact?: VenueContactModel
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  description?: string
  /**
   * 
   * @type {number}
   * @memberof PostVenueBodyModel
   */
  latitude: number
  /**
   * 
   * @type {number}
   * @memberof PostVenueBodyModel
   */
  longitude: number
  /**
   * 
   * @type {number}
   * @memberof PostVenueBodyModel
   */
  managingOffererId: number
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueBodyModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueBodyModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  siret?: string
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  street: string
  /**
   * 
   * @type {number}
   * @memberof PostVenueBodyModel
   */
  venueLabelId?: number
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  venueTypeCode: string
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueBodyModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof PostVenueBodyModel
   */
  withdrawalDetails?: string
}
/**
 * 
 * @export
 * @interface PostVenueProviderBody
 */
export interface PostVenueProviderBody {
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueProviderBody
   */
  isActive?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof PostVenueProviderBody
   */
  isDuo?: boolean
  /**
   * 
   * @type {number}
   * @memberof PostVenueProviderBody
   */
  price?: number
  /**
   * 
   * @type {number}
   * @memberof PostVenueProviderBody
   */
  providerId: number
  /**
   * 
   * @type {number}
   * @memberof PostVenueProviderBody
   */
  quantity?: number
  /**
   * 
   * @type {number}
   * @memberof PostVenueProviderBody
   */
  venueId: number
  /**
   * 
   * @type {string}
   * @memberof PostVenueProviderBody
   */
  venueIdAtOfferProvider?: string
}
/**
 * 
 * @export
 * @interface PriceCategoryBody
 */
export interface PriceCategoryBody {
  /**
   * 
   * @type {Array<CreatePriceCategoryModel | EditPriceCategoryModel>}
   * @memberof PriceCategoryBody
   */
  priceCategories: Array<CreatePriceCategoryModel | EditPriceCategoryModel>
}
/**
 * 
 * @export
 * @interface PriceCategoryResponseModel
 */
export interface PriceCategoryResponseModel {
  /**
   * 
   * @type {number}
   * @memberof PriceCategoryResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof PriceCategoryResponseModel
   */
  label: string
  /**
   * 
   * @type {number}
   * @memberof PriceCategoryResponseModel
   */
  price: number
}
/**
 * 
 * @export
 * @interface ProFlagsQueryModel
 */
export interface ProFlagsQueryModel {
  /**
   * 
   * @type {any}
   * @memberof ProFlagsQueryModel
   */
  firebase: any
}
/**
 * 
 * @export
 * @interface ProUserCreationBodyV2Model
 */
export interface ProUserCreationBodyV2Model {
  /**
   * 
   * @type {boolean}
   * @memberof ProUserCreationBodyV2Model
   */
  contactOk: boolean
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  firstName: string
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  lastName: string
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  password: string
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  phoneNumber: string
  /**
   * 
   * @type {string}
   * @memberof ProUserCreationBodyV2Model
   */
  token: string
}
/**
 * 
 * @export
 * @interface ProviderResponse
 */
export interface ProviderResponse {
  /**
   * 
   * @type {boolean}
   * @memberof ProviderResponse
   */
  hasOffererProvider: boolean
  /**
   * 
   * @type {number}
   * @memberof ProviderResponse
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof ProviderResponse
   */
  isActive: boolean
  /**
   * 
   * @type {string}
   * @memberof ProviderResponse
   */
  name: string
}
/**
 * 
 * @export
 * @interface ReimbursementCsvByInvoicesModel
 */
export interface ReimbursementCsvByInvoicesModel {
  /**
   * 
   * @type {Array<string>}
   * @memberof ReimbursementCsvByInvoicesModel
   */
  invoicesReferences: Array<string>
}
/**
 * 
 * @export
 * @interface ReimbursementCsvQueryModel
 */
export interface ReimbursementCsvQueryModel {
  /**
   * 
   * @type {number}
   * @memberof ReimbursementCsvQueryModel
   */
  bankAccountId?: number
  /**
   * 
   * @type {number}
   * @memberof ReimbursementCsvQueryModel
   */
  offererId: number
  /**
   * 
   * @type {string}
   * @memberof ReimbursementCsvQueryModel
   */
  reimbursementPeriodBeginningDate?: string
  /**
   * 
   * @type {string}
   * @memberof ReimbursementCsvQueryModel
   */
  reimbursementPeriodEndingDate?: string
}
/**
 * 
 * @export
 * @interface ResetPasswordBodyModel
 */
export interface ResetPasswordBodyModel {
  /**
   * 
   * @type {string}
   * @memberof ResetPasswordBodyModel
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof ResetPasswordBodyModel
   */
  token: string
}
/**
 * 
 * @export
 * @interface SaveNewOnboardingDataQueryModel
 */
export interface SaveNewOnboardingDataQueryModel {
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  banId?: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  city: string
  /**
   * 
   * @type {boolean}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  createVenueWithoutSiret?: boolean
  /**
   * 
   * @type {number}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  latitude: number
  /**
   * 
   * @type {number}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  longitude: number
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  postalCode: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  siret: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  street?: string
  /**
   * 
   * @type {Target}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  target: Target
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  token: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  venueTypeCode: string
  /**
   * 
   * @type {string}
   * @memberof SaveNewOnboardingDataQueryModel
   */
  webPresence: string
}
/**
 * 
 * @export
 * @interface SharedCurrentUserResponseModel
 */
export interface SharedCurrentUserResponseModel {
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  activity?: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  address?: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  city?: string
  /**
   * 
   * @type {GenderEnum}
   * @memberof SharedCurrentUserResponseModel
   */
  civility?: GenderEnum
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  dateOfBirth?: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  email: string
  /**
   * 
   * @type {any}
   * @memberof SharedCurrentUserResponseModel
   */
  externalIds?: any
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  firstName?: string
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  hasPartnerPage?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  hasSeenProRgs?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  hasSeenProTutorials?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  hasUserOfferer?: boolean
  /**
   * 
   * @type {number}
   * @memberof SharedCurrentUserResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  idPieceNumber?: string
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  isAdmin: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  isEmailValidated: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  isImpersonated?: boolean
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  lastConnectionDate?: string
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  lastName?: string
  /**
   * 
   * @type {boolean}
   * @memberof SharedCurrentUserResponseModel
   */
  needsToFillCulturalSurvey?: boolean
  /**
   * 
   * @type {any}
   * @memberof SharedCurrentUserResponseModel
   */
  notificationSubscriptions?: any
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {PhoneValidationStatusType}
   * @memberof SharedCurrentUserResponseModel
   */
  phoneValidationStatus?: PhoneValidationStatusType
  /**
   * 
   * @type {string}
   * @memberof SharedCurrentUserResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {Array<UserRole>}
   * @memberof SharedCurrentUserResponseModel
   */
  roles: Array<UserRole>
}
/**
 * 
 * @export
 * @interface SharedLoginUserResponseModel
 */
export interface SharedLoginUserResponseModel {
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  activity?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  address?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  city?: string
  /**
   * 
   * @type {GenderEnum}
   * @memberof SharedLoginUserResponseModel
   */
  civility?: GenderEnum
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  dateCreated: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  dateOfBirth?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  departementCode?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  firstName?: string
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  hasPartnerPage?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  hasSeenProRgs?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  hasSeenProTutorials?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  hasUserOfferer?: boolean
  /**
   * 
   * @type {number}
   * @memberof SharedLoginUserResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  isAdmin: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  isEmailValidated: boolean
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  lastConnectionDate?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  lastName?: string
  /**
   * 
   * @type {boolean}
   * @memberof SharedLoginUserResponseModel
   */
  needsToFillCulturalSurvey?: boolean
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {string}
   * @memberof SharedLoginUserResponseModel
   */
  postalCode?: string
  /**
   * 
   * @type {Array<UserRole>}
   * @memberof SharedLoginUserResponseModel
   */
  roles: Array<UserRole>
}
/**
 * 
 * @export
 * @interface SirenInfo
 */
export interface SirenInfo {
  /**
   * 
   * @type {Address}
   * @memberof SirenInfo
   */
  address: Address
  /**
   * 
   * @type {string}
   * @memberof SirenInfo
   */
  ape_code: string
  /**
   * 
   * @type {string}
   * @memberof SirenInfo
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof SirenInfo
   */
  siren: string
}
/**
 * 
 * @export
 * @interface SiretInfo
 */
export interface SiretInfo {
  /**
   * 
   * @type {boolean}
   * @memberof SiretInfo
   */
  active: boolean
  /**
   * 
   * @type {Address}
   * @memberof SiretInfo
   */
  address: Address
  /**
   * 
   * @type {string}
   * @memberof SiretInfo
   */
  ape_code: string
  /**
   * 
   * @type {string}
   * @memberof SiretInfo
   */
  legal_category_code: string
  /**
   * 
   * @type {string}
   * @memberof SiretInfo
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof SiretInfo
   */
  siret: string
}
/**
 * 
 * @export
 * @interface StatisticsModel
 */
export interface StatisticsModel {
  /**
   * 
   * @type {{ [key: string]: AggregatedRevenue | Map; }}
   * @memberof StatisticsModel
   */
  incomeByYear: { [key: string]: AggregatedRevenue | Map; }
}
/**
 * 
 * @export
 * @interface StatisticsQueryModel
 */
export interface StatisticsQueryModel {
  /**
   * 
   * @type {Array<number> | number}
   * @memberof StatisticsQueryModel
   */
  venue_ids?: Array<number> | number
}
/**
 * 
 * @export
 * @interface Status
 */
export interface Status {
}
/**
 * 
 * @export
 * @interface Status1
 */
export interface Status1 {
}
/**
 * 
 * @export
 * @interface StockCreationBodyModel
 */
export interface StockCreationBodyModel {
  /**
   * 
   * @type {Array<string>}
   * @memberof StockCreationBodyModel
   */
  activationCodes?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof StockCreationBodyModel
   */
  activationCodesExpirationDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof StockCreationBodyModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof StockCreationBodyModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof StockCreationBodyModel
   */
  price?: number
  /**
   * 
   * @type {number}
   * @memberof StockCreationBodyModel
   */
  priceCategoryId?: number
  /**
   * 
   * @type {number}
   * @memberof StockCreationBodyModel
   */
  quantity?: number
}
/**
 * 
 * @export
 * @interface StockEditionBodyModel
 */
export interface StockEditionBodyModel {
  /**
   * 
   * @type {string}
   * @memberof StockEditionBodyModel
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof StockEditionBodyModel
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof StockEditionBodyModel
   */
  id: number
  /**
   * 
   * @type {number}
   * @memberof StockEditionBodyModel
   */
  price?: number
  /**
   * 
   * @type {number}
   * @memberof StockEditionBodyModel
   */
  priceCategoryId?: number
  /**
   * 
   * @type {number}
   * @memberof StockEditionBodyModel
   */
  quantity?: number
}
/**
 * 
 * @export
 * @interface StockIdResponseModel
 */
export interface StockIdResponseModel {
  /**
   * 
   * @type {number}
   * @memberof StockIdResponseModel
   */
  id: number
}
/**
 * 
 * @export
 * @interface StockStatsResponseModel
 */
export interface StockStatsResponseModel {
  /**
   * 
   * @type {string}
   * @memberof StockStatsResponseModel
   */
  newestStock?: string
  /**
   * 
   * @type {string}
   * @memberof StockStatsResponseModel
   */
  oldestStock?: string
  /**
   * 
   * @type {number}
   * @memberof StockStatsResponseModel
   */
  remainingQuantity?: number
  /**
   * 
   * @type {number}
   * @memberof StockStatsResponseModel
   */
  stockCount?: number
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum StocksOrderedBy {
  DATE = <any> 'DATE',
  TIME = <any> 'TIME',
  BEGINNINGDATETIME = <any> 'BEGINNING_DATETIME',
  PRICECATEGORYID = <any> 'PRICE_CATEGORY_ID',
  BOOKINGLIMITDATETIME = <any> 'BOOKING_LIMIT_DATETIME',
  REMAININGQUANTITY = <any> 'REMAINING_QUANTITY',
  DNBOOKEDQUANTITY = <any> 'DN_BOOKED_QUANTITY'
}
/**
 * 
 * @export
 * @interface StocksQueryModel
 */
export interface StocksQueryModel {
  /**
   * 
   * @type {string}
   * @memberof StocksQueryModel
   */
  date?: string
  /**
   * 
   * @type {StocksOrderedBy}
   * @memberof StocksQueryModel
   */
  order_by?: StocksOrderedBy
  /**
   * 
   * @type {boolean}
   * @memberof StocksQueryModel
   */
  order_by_desc?: boolean
  /**
   * 
   * @type {number}
   * @memberof StocksQueryModel
   */
  page?: number
  /**
   * 
   * @type {number}
   * @memberof StocksQueryModel
   */
  price_category_id?: number
  /**
   * 
   * @type {number}
   * @memberof StocksQueryModel
   */
  stocks_limit_per_page?: number
  /**
   * 
   * @type {string}
   * @memberof StocksQueryModel
   */
  time?: string
}
/**
 * 
 * @export
 * @interface StocksResponseModel
 */
export interface StocksResponseModel {
  /**
   * 
   * @type {number}
   * @memberof StocksResponseModel
   */
  stocks_count: number
}
/**
 * 
 * @export
 * @interface StocksUpsertBodyModel
 */
export interface StocksUpsertBodyModel {
  /**
   * 
   * @type {number}
   * @memberof StocksUpsertBodyModel
   */
  offerId: number
  /**
   * 
   * @type {Array<StockCreationBodyModel | StockEditionBodyModel>}
   * @memberof StocksUpsertBodyModel
   */
  stocks: Array<StockCreationBodyModel | StockEditionBodyModel>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum StudentLevels {
  ColesMarseilleMaternelle = <any> 'Écoles Marseille - Maternelle',
  ColesMarseilleCPCE1CE2 = <any> 'Écoles Marseille - CP, CE1, CE2',
  ColesMarseilleCM1CM2 = <any> 'Écoles Marseille - CM1, CM2',
  Collge6e = <any> 'Collège - 6e',
  Collge5e = <any> 'Collège - 5e',
  Collge4e = <any> 'Collège - 4e',
  Collge3e = <any> 'Collège - 3e',
  CAP1reAnne = <any> 'CAP - 1re année',
  CAP2eAnne = <any> 'CAP - 2e année',
  LyceSeconde = <any> 'Lycée - Seconde',
  LycePremire = <any> 'Lycée - Première',
  LyceTerminale = <any> 'Lycée - Terminale'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum SubcategoryIdEnum {
  ABOBIBLIOTHEQUE = <any> 'ABO_BIBLIOTHEQUE',
  ABOCONCERT = <any> 'ABO_CONCERT',
  ABOJEUVIDEO = <any> 'ABO_JEU_VIDEO',
  ABOLIVRENUMERIQUE = <any> 'ABO_LIVRE_NUMERIQUE',
  ABOLUDOTHEQUE = <any> 'ABO_LUDOTHEQUE',
  ABOMEDIATHEQUE = <any> 'ABO_MEDIATHEQUE',
  ABOPLATEFORMEMUSIQUE = <any> 'ABO_PLATEFORME_MUSIQUE',
  ABOPLATEFORMEVIDEO = <any> 'ABO_PLATEFORME_VIDEO',
  ABOPRATIQUEART = <any> 'ABO_PRATIQUE_ART',
  ABOPRESSEENLIGNE = <any> 'ABO_PRESSE_EN_LIGNE',
  ABOSPECTACLE = <any> 'ABO_SPECTACLE',
  ACHATINSTRUMENT = <any> 'ACHAT_INSTRUMENT',
  ACTIVATIONEVENT = <any> 'ACTIVATION_EVENT',
  ACTIVATIONTHING = <any> 'ACTIVATION_THING',
  APPCULTURELLE = <any> 'APP_CULTURELLE',
  ATELIERPRATIQUEART = <any> 'ATELIER_PRATIQUE_ART',
  AUTRESUPPORTNUMERIQUE = <any> 'AUTRE_SUPPORT_NUMERIQUE',
  BONACHATINSTRUMENT = <any> 'BON_ACHAT_INSTRUMENT',
  CAPTATIONMUSIQUE = <any> 'CAPTATION_MUSIQUE',
  CARTECINEILLIMITE = <any> 'CARTE_CINE_ILLIMITE',
  CARTECINEMULTISEANCES = <any> 'CARTE_CINE_MULTISEANCES',
  CARTEJEUNES = <any> 'CARTE_JEUNES',
  CARTEMUSEE = <any> 'CARTE_MUSEE',
  CINEPLEINAIR = <any> 'CINE_PLEIN_AIR',
  CINEVENTEDISTANCE = <any> 'CINE_VENTE_DISTANCE',
  CONCERT = <any> 'CONCERT',
  CONCOURS = <any> 'CONCOURS',
  CONFERENCE = <any> 'CONFERENCE',
  DECOUVERTEMETIERS = <any> 'DECOUVERTE_METIERS',
  ESCAPEGAME = <any> 'ESCAPE_GAME',
  EVENEMENTCINE = <any> 'EVENEMENT_CINE',
  EVENEMENTJEU = <any> 'EVENEMENT_JEU',
  EVENEMENTMUSIQUE = <any> 'EVENEMENT_MUSIQUE',
  EVENEMENTPATRIMOINE = <any> 'EVENEMENT_PATRIMOINE',
  FESTIVALARTVISUEL = <any> 'FESTIVAL_ART_VISUEL',
  FESTIVALCINE = <any> 'FESTIVAL_CINE',
  FESTIVALLIVRE = <any> 'FESTIVAL_LIVRE',
  FESTIVALMUSIQUE = <any> 'FESTIVAL_MUSIQUE',
  FESTIVALSPECTACLE = <any> 'FESTIVAL_SPECTACLE',
  JEUENLIGNE = <any> 'JEU_EN_LIGNE',
  JEUSUPPORTPHYSIQUE = <any> 'JEU_SUPPORT_PHYSIQUE',
  LIVESTREAMEVENEMENT = <any> 'LIVESTREAM_EVENEMENT',
  LIVESTREAMMUSIQUE = <any> 'LIVESTREAM_MUSIQUE',
  LIVESTREAMPRATIQUEARTISTIQUE = <any> 'LIVESTREAM_PRATIQUE_ARTISTIQUE',
  LIVREAUDIOPHYSIQUE = <any> 'LIVRE_AUDIO_PHYSIQUE',
  LIVRENUMERIQUE = <any> 'LIVRE_NUMERIQUE',
  LIVREPAPIER = <any> 'LIVRE_PAPIER',
  LOCATIONINSTRUMENT = <any> 'LOCATION_INSTRUMENT',
  MATERIELARTCREATIF = <any> 'MATERIEL_ART_CREATIF',
  MUSEEVENTEDISTANCE = <any> 'MUSEE_VENTE_DISTANCE',
  OEUVREART = <any> 'OEUVRE_ART',
  PARTITION = <any> 'PARTITION',
  PLATEFORMEPRATIQUEARTISTIQUE = <any> 'PLATEFORME_PRATIQUE_ARTISTIQUE',
  PRATIQUEARTVENTEDISTANCE = <any> 'PRATIQUE_ART_VENTE_DISTANCE',
  PODCAST = <any> 'PODCAST',
  RENCONTREENLIGNE = <any> 'RENCONTRE_EN_LIGNE',
  RENCONTREJEU = <any> 'RENCONTRE_JEU',
  RENCONTRE = <any> 'RENCONTRE',
  SALON = <any> 'SALON',
  SEANCECINE = <any> 'SEANCE_CINE',
  SEANCEESSAIPRATIQUEART = <any> 'SEANCE_ESSAI_PRATIQUE_ART',
  SPECTACLEENREGISTRE = <any> 'SPECTACLE_ENREGISTRE',
  SPECTACLEREPRESENTATION = <any> 'SPECTACLE_REPRESENTATION',
  SPECTACLEVENTEDISTANCE = <any> 'SPECTACLE_VENTE_DISTANCE',
  SUPPORTPHYSIQUEFILM = <any> 'SUPPORT_PHYSIQUE_FILM',
  SUPPORTPHYSIQUEMUSIQUECD = <any> 'SUPPORT_PHYSIQUE_MUSIQUE_CD',
  SUPPORTPHYSIQUEMUSIQUEVINYLE = <any> 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
  TELECHARGEMENTLIVREAUDIO = <any> 'TELECHARGEMENT_LIVRE_AUDIO',
  TELECHARGEMENTMUSIQUE = <any> 'TELECHARGEMENT_MUSIQUE',
  VISITEGUIDEE = <any> 'VISITE_GUIDEE',
  VISITEVIRTUELLE = <any> 'VISITE_VIRTUELLE',
  VISITE = <any> 'VISITE',
  VOD = <any> 'VOD'
}
/**
 * 
 * @export
 * @interface SubcategoryResponseModel
 */
export interface SubcategoryResponseModel {
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  appLabel: string
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  canBeDuo: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  canBeEducational: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  canBeWithdrawable: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  canExpire: boolean
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  categoryId: string
  /**
   * 
   * @type {Array<string>}
   * @memberof SubcategoryResponseModel
   */
  conditionalFields: Array<string>
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  id: string
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  isDigitalDeposit: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  isEvent: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  isPhysicalDeposit: boolean
  /**
   * 
   * @type {boolean}
   * @memberof SubcategoryResponseModel
   */
  isSelectable: boolean
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  onlineOfflinePlatform: string
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  proLabel: string
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  reimbursementRule: string
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  searchGroupName?: string
}
/**
 * 
 * @export
 * @interface SubmitReviewRequestModel
 */
export interface SubmitReviewRequestModel {
  /**
   * 
   * @type {string}
   * @memberof SubmitReviewRequestModel
   */
  location: string
  /**
   * 
   * @type {number}
   * @memberof SubmitReviewRequestModel
   */
  offererId: number
  /**
   * 
   * @type {string}
   * @memberof SubmitReviewRequestModel
   */
  userComment: string
  /**
   * 
   * @type {string}
   * @memberof SubmitReviewRequestModel
   */
  userSatisfaction: string
}
/**
 * 
 * @export
 * @interface SuggestedSubcategoriesQueryModel
 */
export interface SuggestedSubcategoriesQueryModel {
  /**
   * 
   * @type {string}
   * @memberof SuggestedSubcategoriesQueryModel
   */
  offer_description?: string
  /**
   * 
   * @type {string}
   * @memberof SuggestedSubcategoriesQueryModel
   */
  offer_name: string
  /**
   * 
   * @type {number}
   * @memberof SuggestedSubcategoriesQueryModel
   */
  venue_id?: number
}
/**
 * 
 * @export
 * @interface SuggestedSubcategoriesResponseModel
 */
export interface SuggestedSubcategoriesResponseModel {
  /**
   * 
   * @type {string}
   * @memberof SuggestedSubcategoriesResponseModel
   */
  callId: string
  /**
   * 
   * @type {Array<string>}
   * @memberof SuggestedSubcategoriesResponseModel
   */
  subcategoryIds: Array<string>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum Target {
  EDUCATIONAL = <any> 'EDUCATIONAL',
  INDIVIDUALANDEDUCATIONAL = <any> 'INDIVIDUAL_AND_EDUCATIONAL',
  INDIVIDUAL = <any> 'INDIVIDUAL'
}
/**
 * 
 * @export
 * @interface TemplateDatesModel
 */
export interface TemplateDatesModel {
  /**
   * 
   * @type {string}
   * @memberof TemplateDatesModel
   */
  end: string
  /**
   * 
   * @type {string}
   * @memberof TemplateDatesModel
   */
  start: string
}
/**
 * 
 * @export
 * @interface TopOffersResponseData
 */
export interface TopOffersResponseData {
  /**
   * 
   * @type {OfferImage}
   * @memberof TopOffersResponseData
   */
  image?: OfferImage
  /**
   * 
   * @type {number}
   * @memberof TopOffersResponseData
   */
  numberOfViews: number
  /**
   * 
   * @type {number}
   * @memberof TopOffersResponseData
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof TopOffersResponseData
   */
  offerName: string
}
/**
 * 
 * @export
 * @interface UserEmailValidationResponseModel
 */
export interface UserEmailValidationResponseModel {
  /**
   * 
   * @type {string}
   * @memberof UserEmailValidationResponseModel
   */
  newEmail?: string
}
/**
 * 
 * @export
 * @interface UserHasBookingResponse
 */
export interface UserHasBookingResponse {
  /**
   * 
   * @type {boolean}
   * @memberof UserHasBookingResponse
   */
  hasBookings: boolean
}
/**
 * 
 * @export
 * @interface UserIdentityBodyModel
 */
export interface UserIdentityBodyModel {
  /**
   * 
   * @type {string}
   * @memberof UserIdentityBodyModel
   */
  firstName: string
  /**
   * 
   * @type {string}
   * @memberof UserIdentityBodyModel
   */
  lastName: string
}
/**
 * 
 * @export
 * @interface UserIdentityResponseModel
 */
export interface UserIdentityResponseModel {
  /**
   * 
   * @type {string}
   * @memberof UserIdentityResponseModel
   */
  firstName: string
  /**
   * 
   * @type {string}
   * @memberof UserIdentityResponseModel
   */
  lastName: string
}
/**
 * 
 * @export
 * @interface UserPhoneBodyModel
 */
export interface UserPhoneBodyModel {
  /**
   * 
   * @type {string}
   * @memberof UserPhoneBodyModel
   */
  phoneNumber: string
}
/**
 * 
 * @export
 * @interface UserPhoneResponseModel
 */
export interface UserPhoneResponseModel {
  /**
   * 
   * @type {string}
   * @memberof UserPhoneResponseModel
   */
  phoneNumber: string
}
/**
 * 
 * @export
 * @interface UserResetEmailBodyModel
 */
export interface UserResetEmailBodyModel {
  /**
   * 
   * @type {string}
   * @memberof UserResetEmailBodyModel
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof UserResetEmailBodyModel
   */
  password: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum UserRole {
  ADMIN = <any> 'ADMIN',
  ANONYMIZED = <any> 'ANONYMIZED',
  BENEFICIARY = <any> 'BENEFICIARY',
  PRO = <any> 'PRO',
  NONATTACHEDPRO = <any> 'NON_ATTACHED_PRO',
  UNDERAGEBENEFICIARY = <any> 'UNDERAGE_BENEFICIARY',
  TEST = <any> 'TEST'
}
/**
 * Model of a validation error response.
 * @export
 */
export type ValidationError = Array<ValidationErrorElement>
/**
 * Model of a validation error response element.
 * @export
 * @interface ValidationErrorElement
 */
export interface ValidationErrorElement {
  /**
   * 
   * @type {any}
   * @memberof ValidationErrorElement
   */
  ctx?: any
  /**
   * 
   * @type {Array<string>}
   * @memberof ValidationErrorElement
   */
  loc: Array<string>
  /**
   * 
   * @type {string}
   * @memberof ValidationErrorElement
   */
  msg: string
  /**
   * 
   * @type {string}
   * @memberof ValidationErrorElement
   */
  type: string
}
/**
 * 
 * @export
 * @interface VenueContactModel
 */
export interface VenueContactModel {
  /**
   * 
   * @type {string}
   * @memberof VenueContactModel
   */
  email?: string
  /**
   * 
   * @type {string}
   * @memberof VenueContactModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {{ [key: string]: string; }}
   * @memberof VenueContactModel
   */
  socialMedias?: { [key: string]: string; }
  /**
   * 
   * @type {string}
   * @memberof VenueContactModel
   */
  website?: string
}
/**
 * 
 * @export
 * @interface VenueIds
 */
export interface VenueIds {
}
/**
 * 
 * @export
 */
export type VenueLabelListResponseModel = Array<VenueLabelResponseModel>
/**
 * 
 * @export
 * @interface VenueLabelResponseModel
 */
export interface VenueLabelResponseModel {
  /**
   * 
   * @type {number}
   * @memberof VenueLabelResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof VenueLabelResponseModel
   */
  label: string
}
/**
 * 
 * @export
 * @interface VenueListItemResponseModel
 */
export interface VenueListItemResponseModel {
  /**
   * 
   * @type {AddressResponseIsLinkedToVenueModel}
   * @memberof VenueListItemResponseModel
   */
  address?: AddressResponseIsLinkedToVenueModel
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  bookingEmail?: string
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  collectiveSubCategoryId?: string
  /**
   * 
   * @type {ExternalAccessibilityDataModel}
   * @memberof VenueListItemResponseModel
   */
  externalAccessibilityData?: ExternalAccessibilityDataModel
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  hasCreatedOffer: boolean
  /**
   * 
   * @type {number}
   * @memberof VenueListItemResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  isVirtual: boolean
  /**
   * 
   * @type {number}
   * @memberof VenueListItemResponseModel
   */
  managingOffererId: number
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  offererName: string
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  siret?: string
  /**
   * 
   * @type {VenueTypeCode}
   * @memberof VenueListItemResponseModel
   */
  venueTypeCode: VenueTypeCode
  /**
   * 
   * @type {boolean}
   * @memberof VenueListItemResponseModel
   */
  visualDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof VenueListItemResponseModel
   */
  withdrawalDetails?: string
}
/**
 * 
 * @export
 * @interface VenueListQueryModel
 */
export interface VenueListQueryModel {
  /**
   * 
   * @type {boolean}
   * @memberof VenueListQueryModel
   */
  activeOfferersOnly?: boolean
  /**
   * 
   * @type {number}
   * @memberof VenueListQueryModel
   */
  offererId?: number
  /**
   * 
   * @type {boolean}
   * @memberof VenueListQueryModel
   */
  validated?: boolean
}
/**
 * 
 * @export
 * @interface VenueOfOffererFromSiretResponseModel
 */
export interface VenueOfOffererFromSiretResponseModel {
  /**
   * 
   * @type {number}
   * @memberof VenueOfOffererFromSiretResponseModel
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof VenueOfOffererFromSiretResponseModel
   */
  isPermanent: boolean
  /**
   * 
   * @type {string}
   * @memberof VenueOfOffererFromSiretResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof VenueOfOffererFromSiretResponseModel
   */
  publicName?: string
  /**
   * 
   * @type {string}
   * @memberof VenueOfOffererFromSiretResponseModel
   */
  siret?: string
}
/**
 * 
 * @export
 * @interface VenueProviderResponse
 */
export interface VenueProviderResponse {
  /**
   * 
   * @type {string}
   * @memberof VenueProviderResponse
   */
  dateCreated: string
  /**
   * 
   * @type {number}
   * @memberof VenueProviderResponse
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof VenueProviderResponse
   */
  isActive: boolean
  /**
   * 
   * @type {boolean}
   * @memberof VenueProviderResponse
   */
  isDuo?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof VenueProviderResponse
   */
  isFromAllocineProvider: boolean
  /**
   * 
   * @type {string}
   * @memberof VenueProviderResponse
   */
  lastSyncDate?: string
  /**
   * 
   * @type {number}
   * @memberof VenueProviderResponse
   */
  price?: number
  /**
   * 
   * @type {ProviderResponse}
   * @memberof VenueProviderResponse
   */
  provider: ProviderResponse
  /**
   * 
   * @type {number}
   * @memberof VenueProviderResponse
   */
  quantity?: number
  /**
   * 
   * @type {number}
   * @memberof VenueProviderResponse
   */
  venueId: number
  /**
   * 
   * @type {string}
   * @memberof VenueProviderResponse
   */
  venueIdAtOfferProvider?: string
}
/**
 * 
 * @export
 * @interface VenueResponseModel
 */
export interface VenueResponseModel {
  /**
   * 
   * @type {number}
   * @memberof VenueResponseModel
   */
  id: number
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum VenueTypeCode {
  LieuAdministratif = <any> 'Lieu administratif',
  CoursEtPratiqueArtistiques = <any> 'Cours et pratique artistiques',
  Librairie = <any> 'Librairie',
  MusiqueSalleDeConcerts = <any> 'Musique - Salle de concerts',
  MagasinArtsCratifs = <any> 'Magasin arts créatifs',
  CentreCulturel = <any> 'Centre culturel',
  OffreNumrique = <any> 'Offre numérique',
  MagasinDeDistributionDeProduitsCulturels = <any> 'Magasin de distribution de produits culturels',
  Festival = <any> 'Festival',
  JeuxJeuxVidos = <any> 'Jeux / Jeux vidéos',
  BibliothqueOuMdiathque = <any> 'Bibliothèque ou médiathèque',
  CinmaSalleDeProjections = <any> 'Cinéma - Salle de projections',
  Muse = <any> 'Musée',
  MusiqueMagasinDinstruments = <any> 'Musique - Magasin d’instruments',
  Autre = <any> 'Autre',
  PatrimoineEtTourisme = <any> 'Patrimoine et tourisme',
  SpectacleVivant = <any> 'Spectacle vivant',
  MusiqueDisquaire = <any> 'Musique - Disquaire',
  CultureScientifique = <any> 'Culture scientifique',
  CinmaItinrant = <any> 'Cinéma itinérant',
  ArtsVisuelsArtsPlastiquesEtGaleries = <any> 'Arts visuels, arts plastiques et galeries'
}
/**
 * 
 * @export
 */
export type VenueTypeListResponseModel = Array<VenueTypeResponseModel>
/**
 * 
 * @export
 * @interface VenueTypeResponseModel
 */
export interface VenueTypeResponseModel {
  /**
   * 
   * @type {string}
   * @memberof VenueTypeResponseModel
   */
  id: string
  /**
   * 
   * @type {string}
   * @memberof VenueTypeResponseModel
   */
  label: string
}
/**
 * 
 * @export
 * @interface VenuesEducationalStatusResponseModel
 */
export interface VenuesEducationalStatusResponseModel {
  /**
   * 
   * @type {number}
   * @memberof VenuesEducationalStatusResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof VenuesEducationalStatusResponseModel
   */
  name: string
}
/**
 * 
 * @export
 * @interface VenuesEducationalStatusesResponseModel
 */
export interface VenuesEducationalStatusesResponseModel {
  /**
   * 
   * @type {Array<VenuesEducationalStatusResponseModel>}
   * @memberof VenuesEducationalStatusesResponseModel
   */
  statuses: Array<VenuesEducationalStatusResponseModel>
}
/**
 * 
 * @export
 * @interface VisualDisabilityModel
 */
export interface VisualDisabilityModel {
  /**
   * 
   * @type {Array<string>}
   * @memberof VisualDisabilityModel
   */
  audioDescription?: Array<string>
  /**
   * 
   * @type {string}
   * @memberof VisualDisabilityModel
   */
  soundBeacon?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum WithdrawalTypeEnum {
  ByEmail = <any> 'by_email',
  InApp = <any> 'in_app',
  NoTicket = <any> 'no_ticket',
  OnSite = <any> 'on_site'
}
/**
 * DefaultApi - fetch parameter creator
 * @export
 */
export const DefaultApiFetchParamCreator = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary attach_offer_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling attachOfferImage.')
      }
      const localVarPath = `/collective/offers/{offer_id}/image`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarFormParams = new URLSearchParams()


      if (credit !== undefined) {
        localVarFormParams.set('credit', credit as any)
      }

      if (croppingRectHeight !== undefined) {
        localVarFormParams.set('croppingRectHeight', croppingRectHeight as any)
      }

      if (croppingRectWidth !== undefined) {
        localVarFormParams.set('croppingRectWidth', croppingRectWidth as any)
      }

      if (croppingRectX !== undefined) {
        localVarFormParams.set('croppingRectX', croppingRectX as any)
      }

      if (croppingRectY !== undefined) {
        localVarFormParams.set('croppingRectY', croppingRectY as any)
      }

      localVarHeaderParameter['Content-Type'] = 'application/x-www-form-urlencoded'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body = localVarFormParams.toString()

      return localVarRequestOptions
    },
    /**
     * 
     * @summary attach_offer_template_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferTemplateImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling attachOfferTemplateImage.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}/image`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarFormParams = new URLSearchParams()


      if (credit !== undefined) {
        localVarFormParams.set('credit', credit as any)
      }

      if (croppingRectHeight !== undefined) {
        localVarFormParams.set('croppingRectHeight', croppingRectHeight as any)
      }

      if (croppingRectWidth !== undefined) {
        localVarFormParams.set('croppingRectWidth', croppingRectWidth as any)
      }

      if (croppingRectX !== undefined) {
        localVarFormParams.set('croppingRectX', croppingRectX as any)
      }

      if (croppingRectY !== undefined) {
        localVarFormParams.set('croppingRectY', croppingRectY as any)
      }

      localVarHeaderParameter['Content-Type'] = 'application/x-www-form-urlencoded'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body = localVarFormParams.toString()

      return localVarRequestOptions
    },
    /**
     * 
     * @summary cancel_collective_offer_booking <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cancelCollectiveOfferBooking(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling cancelCollectiveOfferBooking.')
      }
      const localVarPath = `/collective/offers/{offer_id}/cancel_booking`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary check_activation_token_exists <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    checkActivationTokenExists(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling checkActivationTokenExists.')
      }
      const localVarPath = `/users/token/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary connect_as <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    connectAs(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling connectAs.')
      }
      const localVarPath = `/users/connect-as/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary cookies_consent <POST>
     * @param {CookieConsentRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cookiesConsent(body?: CookieConsentRequest, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/cookies`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_collective_offer <POST>
     * @param {PostCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOffer(body?: PostCollectiveOfferBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_collective_offer_template <POST>
     * @param {PostCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplate(body?: PostCollectiveOfferTemplateBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers-template`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_collective_offer_template_from_collective_offer <POST>
     * @param {number} offer_id 
     * @param {CollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplateFromCollectiveOffer(offer_id: number, body?: CollectiveOfferTemplateBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling createCollectiveOfferTemplateFromCollectiveOffer.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}/`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_collective_stock <POST>
     * @param {CollectiveStockCreationBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveStock(body?: CollectiveStockCreationBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/stocks`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_offerer <POST>
     * @param {CreateOffererQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOfferer(body?: CreateOffererQueryModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offerers`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_offerer_address <POST>
     * @param {number} offerer_id 
     * @param {OffererAddressRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOffererAddress(offerer_id: number, body?: OffererAddressRequestModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling createOffererAddress.')
      }
      const localVarPath = `/offerers/{offerer_id}/addresses`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_thumbnail <POST>
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {number} [offerId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createThumbnail(credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, offerId?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/thumbnails/`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarFormParams = new URLSearchParams()


      if (credit !== undefined) {
        localVarFormParams.set('credit', credit as any)
      }

      if (croppingRectHeight !== undefined) {
        localVarFormParams.set('croppingRectHeight', croppingRectHeight as any)
      }

      if (croppingRectWidth !== undefined) {
        localVarFormParams.set('croppingRectWidth', croppingRectWidth as any)
      }

      if (croppingRectX !== undefined) {
        localVarFormParams.set('croppingRectX', croppingRectX as any)
      }

      if (croppingRectY !== undefined) {
        localVarFormParams.set('croppingRectY', croppingRectY as any)
      }

      if (offerId !== undefined) {
        localVarFormParams.set('offerId', offerId as any)
      }

      localVarHeaderParameter['Content-Type'] = 'application/x-www-form-urlencoded'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body = localVarFormParams.toString()

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_venue_provider <POST>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createVenueProvider(body?: PostVenueProviderBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/venueProviders`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_all_filtered_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteFilteredStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteAllFilteredStocks(offer_id: number, body?: DeleteFilteredStockListBody, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteAllFilteredStocks.')
      }
      const localVarPath = `/offers/{offer_id}/stocks/all-delete`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_api_key <DELETE>
     * @param {string} api_key_prefix 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteApiKey(api_key_prefix: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'api_key_prefix' is not null or undefined
      if (api_key_prefix === null || api_key_prefix === undefined) {
        throw new RequiredError('api_key_prefix','Required parameter api_key_prefix was null or undefined when calling deleteApiKey.')
      }
      const localVarPath = `/offerers/api_keys/{api_key_prefix}`
        .replace(`{${'api_key_prefix'}}`, encodeURIComponent(String(api_key_prefix)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_draft_offers <POST>
     * @param {DeleteOfferRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteDraftOffers(body?: DeleteOfferRequestBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/delete-draft`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_offer_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferImage(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteOfferImage.')
      }
      const localVarPath = `/collective/offers/{offer_id}/image`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_offer_template_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferTemplateImage(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteOfferTemplateImage.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}/image`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_price_category <DELETE>
     * @param {number} offer_id 
     * @param {number} price_category_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deletePriceCategory(offer_id: number, price_category_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deletePriceCategory.')
      }
      // verify required parameter 'price_category_id' is not null or undefined
      if (price_category_id === null || price_category_id === undefined) {
        throw new RequiredError('price_category_id','Required parameter price_category_id was null or undefined when calling deletePriceCategory.')
      }
      const localVarPath = `/offers/{offer_id}/price_categories/{price_category_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
        .replace(`{${'price_category_id'}}`, encodeURIComponent(String(price_category_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_stock <DELETE>
     * @param {number} stock_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStock(stock_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'stock_id' is not null or undefined
      if (stock_id === null || stock_id === undefined) {
        throw new RequiredError('stock_id','Required parameter stock_id was null or undefined when calling deleteStock.')
      }
      const localVarPath = `/stocks/{stock_id}`
        .replace(`{${'stock_id'}}`, encodeURIComponent(String(stock_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStocks(offer_id: number, body?: DeleteStockListBody, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteStocks.')
      }
      const localVarPath = `/offers/{offer_id}/stocks/delete`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_thumbnail <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteThumbnail(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteThumbnail.')
      }
      const localVarPath = `/offers/thumbnails/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_venue_banner <DELETE>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueBanner(venue_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling deleteVenueBanner.')
      }
      const localVarPath = `/venues/{venue_id}/banner`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_venue_provider <DELETE>
     * @param {number} venue_provider_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueProvider(venue_provider_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_provider_id' is not null or undefined
      if (venue_provider_id === null || venue_provider_id === undefined) {
        throw new RequiredError('venue_provider_id','Required parameter venue_provider_id was null or undefined when calling deleteVenueProvider.')
      }
      const localVarPath = `/venueProviders/{venue_provider_id}`
        .replace(`{${'venue_provider_id'}}`, encodeURIComponent(String(venue_provider_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary duplicate_collective_offer <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    duplicateCollectiveOffer(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling duplicateCollectiveOffer.')
      }
      const localVarPath = `/collective/offers/{offer_id}/duplicate`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary edit_collective_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOffer(offer_id: number, body?: PatchCollectiveOfferBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling editCollectiveOffer.')
      }
      const localVarPath = `/collective/offers/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary edit_collective_offer_template <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOfferTemplate(offer_id: number, body?: PatchCollectiveOfferTemplateBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling editCollectiveOfferTemplate.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary edit_collective_stock <PATCH>
     * @param {number} collective_stock_id 
     * @param {CollectiveStockEditionBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveStock(collective_stock_id: number, body?: CollectiveStockEditionBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'collective_stock_id' is not null or undefined
      if (collective_stock_id === null || collective_stock_id === undefined) {
        throw new RequiredError('collective_stock_id','Required parameter collective_stock_id was null or undefined when calling editCollectiveStock.')
      }
      const localVarPath = `/collective/stocks/{collective_stock_id}`
        .replace(`{${'collective_stock_id'}}`, encodeURIComponent(String(collective_stock_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary edit_venue <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenue(venue_id: number, body?: EditVenueBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling editVenue.')
      }
      const localVarPath = `/venues/{venue_id}`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary edit_venue_collective_data <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueCollectiveDataBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenueCollectiveData(venue_id: number, body?: EditVenueCollectiveDataBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling editVenueCollectiveData.')
      }
      const localVarPath = `/venues/{venue_id}/collective-data`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_csv <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsCsv(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling exportBookingsForOfferAsCsv.')
      }
      // verify required parameter 'status' is not null or undefined
      if (status === null || status === undefined) {
        throw new RequiredError('status','Required parameter status was null or undefined when calling exportBookingsForOfferAsCsv.')
      }
      // verify required parameter 'event_date' is not null or undefined
      if (event_date === null || event_date === undefined) {
        throw new RequiredError('event_date','Required parameter event_date was null or undefined when calling exportBookingsForOfferAsCsv.')
      }
      const localVarPath = `/bookings/offer/{offer_id}/csv`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (status !== undefined) {
        localVarQueryParameter['status'] = status
      }

      if (event_date !== undefined) {
        localVarQueryParameter['event_date'] = (event_date as any).toISOString()
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_excel <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsExcel(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling exportBookingsForOfferAsExcel.')
      }
      // verify required parameter 'status' is not null or undefined
      if (status === null || status === undefined) {
        throw new RequiredError('status','Required parameter status was null or undefined when calling exportBookingsForOfferAsExcel.')
      }
      // verify required parameter 'event_date' is not null or undefined
      if (event_date === null || event_date === undefined) {
        throw new RequiredError('event_date','Required parameter event_date was null or undefined when calling exportBookingsForOfferAsExcel.')
      }
      const localVarPath = `/bookings/offer/{offer_id}/excel`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (status !== undefined) {
        localVarQueryParameter['status'] = status
      }

      if (event_date !== undefined) {
        localVarQueryParameter['event_date'] = (event_date as any).toISOString()
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary fetch_venue_labels <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    fetchVenueLabels(options: any = {}): ApiRequestOptions {
      const localVarPath = `/venue-labels`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_autocomplete_educational_redactors_for_uai <GET>
     * @param {string} uai 
     * @param {string} candidate 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAutocompleteEducationalRedactorsForUai(uai: string, candidate: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'uai' is not null or undefined
      if (uai === null || uai === undefined) {
        throw new RequiredError('uai','Required parameter uai was null or undefined when calling getAutocompleteEducationalRedactorsForUai.')
      }
      // verify required parameter 'candidate' is not null or undefined
      if (candidate === null || candidate === undefined) {
        throw new RequiredError('candidate','Required parameter candidate was null or undefined when calling getAutocompleteEducationalRedactorsForUai.')
      }
      const localVarPath = `/collective/offers/redactors`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (uai !== undefined) {
        localVarQueryParameter['uai'] = uai
      }

      if (candidate !== undefined) {
        localVarQueryParameter['candidate'] = candidate
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_bank_accounts <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBankAccounts(options: any = {}): ApiRequestOptions {
      const localVarPath = `/finance/bank-accounts`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsCsv(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType, options: any = {}): ApiRequestOptions {
      const localVarPath = `/bookings/csv`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (offerId !== undefined) {
        localVarQueryParameter['offerId'] = offerId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = (eventDate as any).toISOString()
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = (bookingPeriodBeginningDate as any).toISOString()
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = (bookingPeriodEndingDate as any).toISOString()
      }

      if (offererAddressId !== undefined) {
        localVarQueryParameter['offererAddressId'] = offererAddressId
      }

      if (exportType !== undefined) {
        localVarQueryParameter['exportType'] = exportType
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter1} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType1} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsExcel(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter1, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType1, options: any = {}): ApiRequestOptions {
      const localVarPath = `/bookings/excel`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (offerId !== undefined) {
        localVarQueryParameter['offerId'] = offerId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = (eventDate as any).toISOString()
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = (bookingPeriodBeginningDate as any).toISOString()
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = (bookingPeriodEndingDate as any).toISOString()
      }

      if (offererAddressId !== undefined) {
        localVarQueryParameter['offererAddressId'] = offererAddressId
      }

      if (exportType !== undefined) {
        localVarQueryParameter['exportType'] = exportType
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter2} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType2} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsPro(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter2, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType2, options: any = {}): ApiRequestOptions {
      const localVarPath = `/bookings/pro`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (offerId !== undefined) {
        localVarQueryParameter['offerId'] = offerId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = (eventDate as any).toISOString()
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = (bookingPeriodBeginningDate as any).toISOString()
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = (bookingPeriodEndingDate as any).toISOString()
      }

      if (offererAddressId !== undefined) {
        localVarQueryParameter['offererAddressId'] = offererAddressId
      }

      if (exportType !== undefined) {
        localVarQueryParameter['exportType'] = exportType
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCategories(options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/categories`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_booking_by_id <GET>
     * @param {number} booking_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingById(booking_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'booking_id' is not null or undefined
      if (booking_id === null || booking_id === undefined) {
        throw new RequiredError('booking_id','Required parameter booking_id was null or undefined when calling getCollectiveBookingById.')
      }
      const localVarPath = `/collective/bookings/{booking_id}`
        .replace(`{${'booking_id'}}`, encodeURIComponent(String(booking_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter3} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsCsv(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter3, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/bookings/csv`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = eventDate
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = bookingPeriodBeginningDate
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = bookingPeriodEndingDate
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter4} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsExcel(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter4, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/bookings/excel`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = eventDate
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = bookingPeriodBeginningDate
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = bookingPeriodEndingDate
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter5} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsPro(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter5, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/bookings/pro`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (eventDate !== undefined) {
        localVarQueryParameter['eventDate'] = eventDate
      }

      if (bookingStatusFilter !== undefined) {
        localVarQueryParameter['bookingStatusFilter'] = bookingStatusFilter
      }

      if (bookingPeriodBeginningDate !== undefined) {
        localVarQueryParameter['bookingPeriodBeginningDate'] = bookingPeriodBeginningDate
      }

      if (bookingPeriodEndingDate !== undefined) {
        localVarQueryParameter['bookingPeriodEndingDate'] = bookingPeriodEndingDate
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffer(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getCollectiveOffer.')
      }
      const localVarPath = `/collective/offers/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offer_request <GET>
     * @param {number} request_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferRequest(request_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'request_id' is not null or undefined
      if (request_id === null || request_id === undefined) {
        throw new RequiredError('request_id','Required parameter request_id was null or undefined when calling getCollectiveOfferRequest.')
      }
      const localVarPath = `/collective/offers-template/request/{request_id}`
        .replace(`{${'request_id'}}`, encodeURIComponent(String(request_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offer_template <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplate(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getCollectiveOfferTemplate.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType} [collectiveOfferType] 
     * @param {Format} [format] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffers(nameOrIsbn?: string, offererId?: number, status?: Status, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType, format?: Format, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (nameOrIsbn !== undefined) {
        localVarQueryParameter['nameOrIsbn'] = nameOrIsbn
      }

      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      if (status !== undefined) {
        localVarQueryParameter['status'] = status
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (categoryId !== undefined) {
        localVarQueryParameter['categoryId'] = categoryId
      }

      if (creationMode !== undefined) {
        localVarQueryParameter['creationMode'] = creationMode
      }

      if (periodBeginningDate !== undefined) {
        localVarQueryParameter['periodBeginningDate'] = (periodBeginningDate as any).toISOString()
      }

      if (periodEndingDate !== undefined) {
        localVarQueryParameter['periodEndingDate'] = (periodEndingDate as any).toISOString()
      }

      if (collectiveOfferType !== undefined) {
        localVarQueryParameter['collectiveOfferType'] = collectiveOfferType
      }

      if (format !== undefined) {
        localVarQueryParameter['format'] = format
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_combined_invoices <GET>
     * @param {Array<string>} invoiceReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCombinedInvoices(invoiceReferences: Array<string>, options: any = {}): ApiRequestOptions {
      // verify required parameter 'invoiceReferences' is not null or undefined
      if (invoiceReferences === null || invoiceReferences === undefined) {
        throw new RequiredError('invoiceReferences','Required parameter invoiceReferences was null or undefined when calling getCombinedInvoices.')
      }
      const localVarPath = `/finance/combined-invoices`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (invoiceReferences) {
        localVarQueryParameter['invoiceReferences'] = invoiceReferences
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_educational_institutions <GET>
     * @param {number} [perPageLimit] 
     * @param {number} [page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutions(perPageLimit?: number, page?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/educational_institutions`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (perPageLimit !== undefined) {
        localVarQueryParameter['perPageLimit'] = perPageLimit
      }

      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_educational_partners <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalPartners(options: any = {}): ApiRequestOptions {
      const localVarPath = `/cultural-partners`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_invoices_v2 <GET>
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {number} [bankAccountId] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getInvoicesV2(periodBeginningDate?: string, periodEndingDate?: string, bankAccountId?: number, offererId?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/v2/finance/invoices`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (periodBeginningDate !== undefined) {
        localVarQueryParameter['periodBeginningDate'] = (periodBeginningDate as any).toISOString()
      }

      if (periodEndingDate !== undefined) {
        localVarQueryParameter['periodEndingDate'] = (periodEndingDate as any).toISOString()
      }

      if (bankAccountId !== undefined) {
        localVarQueryParameter['bankAccountId'] = bankAccountId
      }

      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_music_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getMusicTypes(options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/music-types`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_national_programs <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNationalPrograms(options: any = {}): ApiRequestOptions {
      const localVarPath = `/national-programs`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffer(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getOffer.')
      }
      const localVarPath = `/offers/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offer_price_categories_and_schedules_by_dates <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferPriceCategoriesAndSchedulesByDates(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getOfferPriceCategoriesAndSchedulesByDates.')
      }
      const localVarPath = `/bookings/dates/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferer(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOfferer.')
      }
      const localVarPath = `/offerers/{offerer_id}`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_addresses <GET>
     * @param {number} offerer_id 
     * @param {boolean} [onlyWithOffers] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererAddresses(offerer_id: number, onlyWithOffers?: boolean, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererAddresses.')
      }
      const localVarPath = `/offerers/{offerer_id}/addresses`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (onlyWithOffers !== undefined) {
        localVarQueryParameter['onlyWithOffers'] = onlyWithOffers
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_bank_accounts_and_attached_venues <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererBankAccountsAndAttachedVenues(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererBankAccountsAndAttachedVenues.')
      }
      const localVarPath = `/offerers/{offerer_id}/bank-accounts`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_members <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererMembers(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererMembers.')
      }
      const localVarPath = `/offerers/{offerer_id}/members`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStats(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererStats.')
      }
      const localVarPath = `/offerers/{offerer_id}/stats`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_stats_dashboard_url <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStatsDashboardUrl(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererStatsDashboardUrl.')
      }
      const localVarPath = `/offerers/{offerer_id}/dashboard`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_offerer_v2_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererV2Stats(offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getOffererV2Stats.')
      }
      const localVarPath = `/offerers/{offerer_id}/v2/stats`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_product_by_ean <GET>
     * @param {string} ean 
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProductByEan(ean: string, offerer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'ean' is not null or undefined
      if (ean === null || ean === undefined) {
        throw new RequiredError('ean','Required parameter ean was null or undefined when calling getProductByEan.')
      }
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling getProductByEan.')
      }
      const localVarPath = `/get_product_by_ean/{ean}/{offerer_id}`
        .replace(`{${'ean'}}`, encodeURIComponent(String(ean)))
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_profile <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProfile(options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/current`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_providers_by_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProvidersByVenue(venue_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling getProvidersByVenue.')
      }
      const localVarPath = `/venueProviders/{venue_id}`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_reimbursements_csv <GET>
     * @param {number} offererId 
     * @param {number} [bankAccountId] 
     * @param {string} [reimbursementPeriodBeginningDate] 
     * @param {string} [reimbursementPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsv(offererId: number, bankAccountId?: number, reimbursementPeriodBeginningDate?: string, reimbursementPeriodEndingDate?: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offererId' is not null or undefined
      if (offererId === null || offererId === undefined) {
        throw new RequiredError('offererId','Required parameter offererId was null or undefined when calling getReimbursementsCsv.')
      }
      const localVarPath = `/reimbursements/csv`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      if (bankAccountId !== undefined) {
        localVarQueryParameter['bankAccountId'] = bankAccountId
      }

      if (reimbursementPeriodBeginningDate !== undefined) {
        localVarQueryParameter['reimbursementPeriodBeginningDate'] = reimbursementPeriodBeginningDate
      }

      if (reimbursementPeriodEndingDate !== undefined) {
        localVarQueryParameter['reimbursementPeriodEndingDate'] = reimbursementPeriodEndingDate
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_reimbursements_csv_v2 <GET>
     * @param {Array<string>} invoicesReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsvV2(invoicesReferences: Array<string>, options: any = {}): ApiRequestOptions {
      // verify required parameter 'invoicesReferences' is not null or undefined
      if (invoicesReferences === null || invoicesReferences === undefined) {
        throw new RequiredError('invoicesReferences','Required parameter invoicesReferences was null or undefined when calling getReimbursementsCsvV2.')
      }
      const localVarPath = `/v2/reimbursements/csv`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (invoicesReferences) {
        localVarQueryParameter['invoicesReferences'] = invoicesReferences
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_siren_info <GET>
     * @param {string} siren 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSirenInfo(siren: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'siren' is not null or undefined
      if (siren === null || siren === undefined) {
        throw new RequiredError('siren','Required parameter siren was null or undefined when calling getSirenInfo.')
      }
      const localVarPath = `/sirene/siren/{siren}`
        .replace(`{${'siren'}}`, encodeURIComponent(String(siren)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_siret_info <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSiretInfo(siret: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'siret' is not null or undefined
      if (siret === null || siret === undefined) {
        throw new RequiredError('siret','Required parameter siret was null or undefined when calling getSiretInfo.')
      }
      const localVarPath = `/sirene/siret/{siret}`
        .replace(`{${'siret'}}`, encodeURIComponent(String(siret)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_statistics <GET>
     * @param {VenueIds} [venue_ids] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStatistics(venue_ids?: VenueIds, options: any = {}): ApiRequestOptions {
      const localVarPath = `/get-statistics`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (venue_ids !== undefined) {
        localVarQueryParameter['venue_ids'] = venue_ids
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_stocks <GET>
     * @param {number} offer_id 
     * @param {string} [date] 
     * @param {string} [time] 
     * @param {number} [price_category_id] 
     * @param {OrderBy} [order_by] 
     * @param {boolean} [order_by_desc] 
     * @param {number} [page] 
     * @param {number} [stocks_limit_per_page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocks(offer_id: number, date?: string, time?: string, price_category_id?: number, order_by?: OrderBy, order_by_desc?: boolean, page?: number, stocks_limit_per_page?: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getStocks.')
      }
      const localVarPath = `/offers/{offer_id}/stocks/`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (date !== undefined) {
        localVarQueryParameter['date'] = (date as any).toISOString()
      }

      if (time !== undefined) {
        localVarQueryParameter['time'] = time
      }

      if (price_category_id !== undefined) {
        localVarQueryParameter['price_category_id'] = price_category_id
      }

      if (order_by !== undefined) {
        localVarQueryParameter['order_by'] = order_by
      }

      if (order_by_desc !== undefined) {
        localVarQueryParameter['order_by_desc'] = order_by_desc
      }

      if (page !== undefined) {
        localVarQueryParameter['page'] = page
      }

      if (stocks_limit_per_page !== undefined) {
        localVarQueryParameter['stocks_limit_per_page'] = stocks_limit_per_page
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_stocks_stats <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocksStats(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling getStocksStats.')
      }
      const localVarPath = `/offers/{offer_id}/stocks-stats`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_suggested_subcategories <GET>
     * @param {string} offer_name 
     * @param {string} [offer_description] 
     * @param {number} [venue_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSuggestedSubcategories(offer_name: string, offer_description?: string, venue_id?: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_name' is not null or undefined
      if (offer_name === null || offer_name === undefined) {
        throw new RequiredError('offer_name','Required parameter offer_name was null or undefined when calling getSuggestedSubcategories.')
      }
      const localVarPath = `/offers/suggested-subcategories`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (offer_name !== undefined) {
        localVarQueryParameter['offer_name'] = offer_name
      }

      if (offer_description !== undefined) {
        localVarQueryParameter['offer_description'] = offer_description
      }

      if (venue_id !== undefined) {
        localVarQueryParameter['venue_id'] = venue_id
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_user_email_pending_validation <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserEmailPendingValidation(options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/email_pending_validation`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_user_has_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasBookings(options: any = {}): ApiRequestOptions {
      const localVarPath = `/bookings/pro/userHasBookings`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_user_has_collective_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasCollectiveBookings(options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/bookings/pro/userHasBookings`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenue(venue_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling getVenue.')
      }
      const localVarPath = `/venues/{venue_id}`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venue_stats_dashboard_url <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueStatsDashboardUrl(venue_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling getVenueStatsDashboardUrl.')
      }
      const localVarPath = `/venues/{venue_id}/dashboard`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venue_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueTypes(options: any = {}): ApiRequestOptions {
      const localVarPath = `/venue-types`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venues <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [activeOfferersOnly] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenues(validated?: boolean, activeOfferersOnly?: boolean, offererId?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/venues`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (validated !== undefined) {
        localVarQueryParameter['validated'] = validated
      }

      if (activeOfferersOnly !== undefined) {
        localVarQueryParameter['activeOfferersOnly'] = activeOfferersOnly
      }

      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venues_educational_statuses <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesEducationalStatuses(options: any = {}): ApiRequestOptions {
      const localVarPath = `/venues-educational-statuses`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venues_of_offerer_from_siret <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesOfOffererFromSiret(siret: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'siret' is not null or undefined
      if (siret === null || siret === undefined) {
        throw new RequiredError('siret','Required parameter siret was null or undefined when calling getVenuesOfOffererFromSiret.')
      }
      const localVarPath = `/venues/siret/{siret}`
        .replace(`{${'siret'}}`, encodeURIComponent(String(siret)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary has_invoice <GET>
     * @param {number} offererId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    hasInvoice(offererId: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offererId' is not null or undefined
      if (offererId === null || offererId === undefined) {
        throw new RequiredError('offererId','Required parameter offererId was null or undefined when calling hasInvoice.')
      }
      const localVarPath = `/v2/finance/has-invoice`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary invite_member <POST>
     * @param {number} offerer_id 
     * @param {InviteMemberQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    inviteMember(offerer_id: number, body?: InviteMemberQueryModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling inviteMember.')
      }
      const localVarPath = `/offerers/{offerer_id}/invite`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary link_venue_to_bank_account <PATCH>
     * @param {number} offerer_id 
     * @param {number} bank_account_id 
     * @param {LinkVenueToBankAccountBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToBankAccount(offerer_id: number, bank_account_id: number, body?: LinkVenueToBankAccountBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offerer_id' is not null or undefined
      if (offerer_id === null || offerer_id === undefined) {
        throw new RequiredError('offerer_id','Required parameter offerer_id was null or undefined when calling linkVenueToBankAccount.')
      }
      // verify required parameter 'bank_account_id' is not null or undefined
      if (bank_account_id === null || bank_account_id === undefined) {
        throw new RequiredError('bank_account_id','Required parameter bank_account_id was null or undefined when calling linkVenueToBankAccount.')
      }
      const localVarPath = `/offerers/{offerer_id}/bank-accounts/{bank_account_id}`
        .replace(`{${'offerer_id'}}`, encodeURIComponent(String(offerer_id)))
        .replace(`{${'bank_account_id'}}`, encodeURIComponent(String(bank_account_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary link_venue_to_pricing_point <POST>
     * @param {number} venue_id 
     * @param {LinkVenueToPricingPointBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToPricingPoint(venue_id: number, body?: LinkVenueToPricingPointBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling linkVenueToPricingPoint.')
      }
      const localVarPath = `/venues/{venue_id}/pricing-point`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_educational_domains <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalDomains(options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/educational-domains`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_educational_offerers <GET>
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalOfferers(offerer_id?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offerers/educational`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (offerer_id !== undefined) {
        localVarQueryParameter['offerer_id'] = offerer_id
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_features <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listFeatures(options: any = {}): ApiRequestOptions {
      const localVarPath = `/features`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_offerers_names <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [validated_for_user] 
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOfferersNames(validated?: boolean, validated_for_user?: boolean, offerer_id?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offerers/names`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (validated !== undefined) {
        localVarQueryParameter['validated'] = validated
      }

      if (validated_for_user !== undefined) {
        localVarQueryParameter['validated_for_user'] = validated_for_user
      }

      if (offerer_id !== undefined) {
        localVarQueryParameter['offerer_id'] = offerer_id
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status1} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType1} [collectiveOfferType] 
     * @param {number} [offererAddressId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOffers(nameOrIsbn?: string, offererId?: number, status?: Status1, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType1, offererAddressId?: number, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (nameOrIsbn !== undefined) {
        localVarQueryParameter['nameOrIsbn'] = nameOrIsbn
      }

      if (offererId !== undefined) {
        localVarQueryParameter['offererId'] = offererId
      }

      if (status !== undefined) {
        localVarQueryParameter['status'] = status
      }

      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      if (categoryId !== undefined) {
        localVarQueryParameter['categoryId'] = categoryId
      }

      if (creationMode !== undefined) {
        localVarQueryParameter['creationMode'] = creationMode
      }

      if (periodBeginningDate !== undefined) {
        localVarQueryParameter['periodBeginningDate'] = (periodBeginningDate as any).toISOString()
      }

      if (periodEndingDate !== undefined) {
        localVarQueryParameter['periodEndingDate'] = (periodEndingDate as any).toISOString()
      }

      if (collectiveOfferType !== undefined) {
        localVarQueryParameter['collectiveOfferType'] = collectiveOfferType
      }

      if (offererAddressId !== undefined) {
        localVarQueryParameter['offererAddressId'] = offererAddressId
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary list_venue_providers <GET>
     * @param {number} venueId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listVenueProviders(venueId: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venueId' is not null or undefined
      if (venueId === null || venueId === undefined) {
        throw new RequiredError('venueId','Required parameter venueId was null or undefined when calling listVenueProviders.')
      }
      const localVarPath = `/venueProviders`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      if (venueId !== undefined) {
        localVarQueryParameter['venueId'] = venueId
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_all_offers_active_status <PATCH>
     * @param {PatchAllOffersActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchAllOffersActiveStatus(body?: PatchAllOffersActiveStatusBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/all-active-status`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offer_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferPublication(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling patchCollectiveOfferPublication.')
      }
      const localVarPath = `/collective/offers/{offer_id}/publish`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offer_template_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferTemplatePublication(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling patchCollectiveOfferTemplatePublication.')
      }
      const localVarPath = `/collective/offers-template/{offer_id}/publish`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offers_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers/active-status`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offers_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersArchive(body?: PatchCollectiveOfferArchiveBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers/archive`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offers_educational_institution <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferEducationalInstitution} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersEducationalInstitution(offer_id: number, body?: PatchCollectiveOfferEducationalInstitution, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling patchCollectiveOffersEducationalInstitution.')
      }
      const localVarPath = `/collective/offers/{offer_id}/educational_institution`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offers_template_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers-template/active-status`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_collective_offers_template_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateArchive(body?: PatchCollectiveOfferArchiveBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/collective/offers-template/archive`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_draft_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchDraftOffer(offer_id: number, body?: PatchDraftOfferBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling patchDraftOffer.')
      }
      const localVarPath = `/offers/draft/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffer(offer_id: number, body?: PatchOfferBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling patchOffer.')
      }
      const localVarPath = `/offers/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_offers_active_status <PATCH>
     * @param {PatchOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffersActiveStatus(body?: PatchOfferActiveStatusBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/active-status`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_pro_user_rgs_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchProUserRgsSeen(options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/rgs-seen`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_publish_offer <PATCH>
     * @param {PatchOfferPublishBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchPublishOffer(body?: PatchOfferPublishBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/publish`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_user_identity <PATCH>
     * @param {UserIdentityBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserIdentity(body?: UserIdentityBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/identity`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_user_phone <PATCH>
     * @param {UserPhoneBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserPhone(body?: UserPhoneBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/phone`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_user_tuto_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserTutoSeen(options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/tuto-seen`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary patch_validate_email <PATCH>
     * @param {ChangeProEmailBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchValidateEmail(body?: ChangeProEmailBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/validate_email`
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_change_password <POST>
     * @param {ChangePasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postChangePassword(body?: ChangePasswordBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/password`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_create_venue <POST>
     * @param {PostVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCreateVenue(body?: PostVenueBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/venues`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_draft_offer <POST>
     * @param {PostDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postDraftOffer(body?: PostDraftOfferBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers/draft`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_new_password <POST>
     * @param {NewPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postNewPassword(body?: NewPasswordBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/new-password`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_offer <POST>
     * @param {PostOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postOffer(body?: PostOfferBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offers`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_price_categories <POST>
     * @param {number} offer_id 
     * @param {PriceCategoryBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postPriceCategories(offer_id: number, body?: PriceCategoryBody, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling postPriceCategories.')
      }
      const localVarPath = `/offers/{offer_id}/price_categories`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_pro_flags <POST>
     * @param {ProFlagsQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postProFlags(body?: ProFlagsQueryModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/pro_flags`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_user_email <POST>
     * @param {UserResetEmailBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postUserEmail(body?: UserResetEmailBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/email`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary reset_password <POST>
     * @param {ResetPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    resetPassword(body?: ResetPasswordBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/reset-password`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary save_new_onboarding_data <POST>
     * @param {SaveNewOnboardingDataQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveNewOnboardingData(body?: SaveNewOnboardingDataQueryModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/offerers/new`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary signin <POST>
     * @param {LoginUserBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signin(body?: LoginUserBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/signin`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary signout <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signout(options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/signout`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary signup_pro_V2 <POST>
     * @param {ProUserCreationBodyV2Model} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signupProV2(body?: ProUserCreationBodyV2Model, options: any = {}): ApiRequestOptions {
      const localVarPath = `/v2/users/signup/pro`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary submit_user_review <POST>
     * @param {SubmitReviewRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    submitUserReview(body?: SubmitReviewRequestModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/users/log-user-review`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary update_venue_provider <PUT>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateVenueProvider(body?: PostVenueProviderBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/venueProviders`
      const localVarRequestOptions = Object.assign({ method: 'PUT', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary upsert_stocks <POST>
     * @param {StocksUpsertBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    upsertStocks(body?: StocksUpsertBodyModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/stocks/bulk`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary validate_user <PATCH>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    validateUser(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling validateUser.')
      }
      const localVarPath = `/validate/user/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
  }
}

/**
 * DefaultApi - functional programming interface
 * @export
 */
export const DefaultApiFp = function(configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary attach_offer_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any): CancelablePromise<AttachImageResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).attachOfferImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary attach_offer_template_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferTemplateImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any): CancelablePromise<AttachImageResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).attachOfferTemplateImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary cancel_collective_offer_booking <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cancelCollectiveOfferBooking(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).cancelCollectiveOfferBooking(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary check_activation_token_exists <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    checkActivationTokenExists(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).checkActivationTokenExists(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary connect_as <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    connectAs(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).connectAs(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary cookies_consent <POST>
     * @param {CookieConsentRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cookiesConsent(body?: CookieConsentRequest, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).cookiesConsent(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_collective_offer <POST>
     * @param {PostCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOffer(body?: PostCollectiveOfferBodyModel, options?: any): CancelablePromise<CollectiveOfferResponseIdModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createCollectiveOffer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_collective_offer_template <POST>
     * @param {PostCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplate(body?: PostCollectiveOfferTemplateBodyModel, options?: any): CancelablePromise<CollectiveOfferResponseIdModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createCollectiveOfferTemplate(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_collective_offer_template_from_collective_offer <POST>
     * @param {number} offer_id 
     * @param {CollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplateFromCollectiveOffer(offer_id: number, body?: CollectiveOfferTemplateBodyModel, options?: any): CancelablePromise<CollectiveOfferTemplateResponseIdModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createCollectiveOfferTemplateFromCollectiveOffer(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_collective_stock <POST>
     * @param {CollectiveStockCreationBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveStock(body?: CollectiveStockCreationBodyModel, options?: any): CancelablePromise<CollectiveStockResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createCollectiveStock(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_offerer <POST>
     * @param {CreateOffererQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOfferer(body?: CreateOffererQueryModel, options?: any): CancelablePromise<PostOffererResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createOfferer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_offerer_address <POST>
     * @param {number} offerer_id 
     * @param {OffererAddressRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOffererAddress(offerer_id: number, body?: OffererAddressRequestModel, options?: any): CancelablePromise<OffererAddressResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createOffererAddress(offerer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_thumbnail <POST>
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {number} [offerId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createThumbnail(credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, offerId?: number, options?: any): CancelablePromise<CreateThumbnailResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createThumbnail(credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, offerId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_venue_provider <POST>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createVenueProvider(body?: PostVenueProviderBody, options?: any): CancelablePromise<VenueProviderResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createVenueProvider(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_all_filtered_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteFilteredStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteAllFilteredStocks(offer_id: number, body?: DeleteFilteredStockListBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteAllFilteredStocks(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_api_key <DELETE>
     * @param {string} api_key_prefix 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteApiKey(api_key_prefix: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteApiKey(api_key_prefix, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_draft_offers <POST>
     * @param {DeleteOfferRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteDraftOffers(body?: DeleteOfferRequestBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteDraftOffers(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_offer_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferImage(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteOfferImage(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_offer_template_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferTemplateImage(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteOfferTemplateImage(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_price_category <DELETE>
     * @param {number} offer_id 
     * @param {number} price_category_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deletePriceCategory(offer_id: number, price_category_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deletePriceCategory(offer_id, price_category_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_stock <DELETE>
     * @param {number} stock_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStock(stock_id: number, options?: any): CancelablePromise<StockIdResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteStock(stock_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStocks(offer_id: number, body?: DeleteStockListBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteStocks(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_thumbnail <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteThumbnail(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteThumbnail(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_venue_banner <DELETE>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueBanner(venue_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteVenueBanner(venue_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_venue_provider <DELETE>
     * @param {number} venue_provider_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueProvider(venue_provider_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteVenueProvider(venue_provider_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary duplicate_collective_offer <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    duplicateCollectiveOffer(offer_id: number, options?: any): CancelablePromise<GetCollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).duplicateCollectiveOffer(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary edit_collective_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOffer(offer_id: number, body?: PatchCollectiveOfferBodyModel, options?: any): CancelablePromise<GetCollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).editCollectiveOffer(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary edit_collective_offer_template <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOfferTemplate(offer_id: number, body?: PatchCollectiveOfferTemplateBodyModel, options?: any): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).editCollectiveOfferTemplate(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary edit_collective_stock <PATCH>
     * @param {number} collective_stock_id 
     * @param {CollectiveStockEditionBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveStock(collective_stock_id: number, body?: CollectiveStockEditionBodyModel, options?: any): CancelablePromise<CollectiveStockResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).editCollectiveStock(collective_stock_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary edit_venue <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenue(venue_id: number, body?: EditVenueBodyModel, options?: any): CancelablePromise<GetVenueResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).editVenue(venue_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary edit_venue_collective_data <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueCollectiveDataBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenueCollectiveData(venue_id: number, body?: EditVenueCollectiveDataBodyModel, options?: any): CancelablePromise<GetVenueResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).editVenueCollectiveData(venue_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_csv <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsCsv(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).exportBookingsForOfferAsCsv(offer_id, status, event_date, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_excel <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsExcel(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).exportBookingsForOfferAsExcel(offer_id, status, event_date, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary fetch_venue_labels <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    fetchVenueLabels(options?: any): CancelablePromise<VenueLabelListResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).fetchVenueLabels(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_autocomplete_educational_redactors_for_uai <GET>
     * @param {string} uai 
     * @param {string} candidate 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAutocompleteEducationalRedactorsForUai(uai: string, candidate: string, options?: any): CancelablePromise<EducationalRedactors> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getAutocompleteEducationalRedactorsForUai(uai, candidate, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_bank_accounts <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBankAccounts(options?: any): CancelablePromise<FinanceBankAccountListResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getBankAccounts(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsCsv(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getBookingsCsv(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter1} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType1} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsExcel(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter1, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType1, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getBookingsExcel(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter2} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType2} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsPro(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter2, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType2, options?: any): CancelablePromise<ListBookingsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getBookingsPro(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCategories(options?: any): CancelablePromise<CategoriesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCategories(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_booking_by_id <GET>
     * @param {number} booking_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingById(booking_id: number, options?: any): CancelablePromise<CollectiveBookingByIdResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveBookingById(booking_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter3} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsCsv(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter3, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveBookingsCsv(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter4} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsExcel(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter4, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveBookingsExcel(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter5} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsPro(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter5, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any): CancelablePromise<ListCollectiveBookingsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveBookingsPro(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffer(offer_id: number, options?: any): CancelablePromise<GetCollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOffer(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer_request <GET>
     * @param {number} request_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferRequest(request_id: number, options?: any): CancelablePromise<GetCollectiveOfferRequestResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOfferRequest(request_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer_template <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplate(offer_id: number, options?: any): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOfferTemplate(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType} [collectiveOfferType] 
     * @param {Format} [format] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffers(nameOrIsbn?: string, offererId?: number, status?: Status, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType, format?: Format, options?: any): CancelablePromise<ListCollectiveOffersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, format, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_combined_invoices <GET>
     * @param {Array<string>} invoiceReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCombinedInvoices(invoiceReferences: Array<string>, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCombinedInvoices(invoiceReferences, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_educational_institutions <GET>
     * @param {number} [perPageLimit] 
     * @param {number} [page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutions(perPageLimit?: number, page?: number, options?: any): CancelablePromise<EducationalInstitutionsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getEducationalInstitutions(perPageLimit, page, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_educational_partners <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalPartners(options?: any): CancelablePromise<AdageCulturalPartnersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getEducationalPartners(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_invoices_v2 <GET>
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {number} [bankAccountId] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getInvoicesV2(periodBeginningDate?: string, periodEndingDate?: string, bankAccountId?: number, offererId?: number, options?: any): CancelablePromise<InvoiceListV2ResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getInvoicesV2(periodBeginningDate, periodEndingDate, bankAccountId, offererId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_music_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getMusicTypes(options?: any): CancelablePromise<GetMusicTypesResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getMusicTypes(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_national_programs <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNationalPrograms(options?: any): CancelablePromise<ListNationalProgramsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getNationalPrograms(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffer(offer_id: number, options?: any): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffer(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offer_price_categories_and_schedules_by_dates <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferPriceCategoriesAndSchedulesByDates(offer_id: number, options?: any): CancelablePromise<EventDatesInfos> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOfferPriceCategoriesAndSchedulesByDates(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferer(offerer_id: number, options?: any): CancelablePromise<GetOffererResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOfferer(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_addresses <GET>
     * @param {number} offerer_id 
     * @param {boolean} [onlyWithOffers] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererAddresses(offerer_id: number, onlyWithOffers?: boolean, options?: any): CancelablePromise<GetOffererAddressesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererAddresses(offerer_id, onlyWithOffers, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_bank_accounts_and_attached_venues <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererBankAccountsAndAttachedVenues(offerer_id: number, options?: any): CancelablePromise<GetOffererBankAccountsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererBankAccountsAndAttachedVenues(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_members <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererMembers(offerer_id: number, options?: any): CancelablePromise<GetOffererMembersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererMembers(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStats(offerer_id: number, options?: any): CancelablePromise<GetOffererStatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererStats(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_stats_dashboard_url <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStatsDashboardUrl(offerer_id: number, options?: any): CancelablePromise<OffererStatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererStatsDashboardUrl(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_offerer_v2_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererV2Stats(offerer_id: number, options?: any): CancelablePromise<GetOffererV2StatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getOffererV2Stats(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_product_by_ean <GET>
     * @param {string} ean 
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProductByEan(ean: string, offerer_id: number, options?: any): CancelablePromise<GetProductInformations> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getProductByEan(ean, offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_profile <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProfile(options?: any): CancelablePromise<SharedCurrentUserResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getProfile(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_providers_by_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProvidersByVenue(venue_id: number, options?: any): CancelablePromise<ListProviderResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getProvidersByVenue(venue_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_reimbursements_csv <GET>
     * @param {number} offererId 
     * @param {number} [bankAccountId] 
     * @param {string} [reimbursementPeriodBeginningDate] 
     * @param {string} [reimbursementPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsv(offererId: number, bankAccountId?: number, reimbursementPeriodBeginningDate?: string, reimbursementPeriodEndingDate?: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getReimbursementsCsv(offererId, bankAccountId, reimbursementPeriodBeginningDate, reimbursementPeriodEndingDate, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_reimbursements_csv_v2 <GET>
     * @param {Array<string>} invoicesReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsvV2(invoicesReferences: Array<string>, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getReimbursementsCsvV2(invoicesReferences, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_siren_info <GET>
     * @param {string} siren 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSirenInfo(siren: string, options?: any): CancelablePromise<SirenInfo> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getSirenInfo(siren, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_siret_info <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSiretInfo(siret: string, options?: any): CancelablePromise<SiretInfo> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getSiretInfo(siret, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_statistics <GET>
     * @param {VenueIds} [venue_ids] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStatistics(venue_ids?: VenueIds, options?: any): CancelablePromise<StatisticsModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getStatistics(venue_ids, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_stocks <GET>
     * @param {number} offer_id 
     * @param {string} [date] 
     * @param {string} [time] 
     * @param {number} [price_category_id] 
     * @param {OrderBy} [order_by] 
     * @param {boolean} [order_by_desc] 
     * @param {number} [page] 
     * @param {number} [stocks_limit_per_page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocks(offer_id: number, date?: string, time?: string, price_category_id?: number, order_by?: OrderBy, order_by_desc?: boolean, page?: number, stocks_limit_per_page?: number, options?: any): CancelablePromise<GetStocksResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getStocks(offer_id, date, time, price_category_id, order_by, order_by_desc, page, stocks_limit_per_page, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_stocks_stats <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocksStats(offer_id: number, options?: any): CancelablePromise<StockStatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getStocksStats(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_suggested_subcategories <GET>
     * @param {string} offer_name 
     * @param {string} [offer_description] 
     * @param {number} [venue_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSuggestedSubcategories(offer_name: string, offer_description?: string, venue_id?: number, options?: any): CancelablePromise<SuggestedSubcategoriesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getSuggestedSubcategories(offer_name, offer_description, venue_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_user_email_pending_validation <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserEmailPendingValidation(options?: any): CancelablePromise<UserEmailValidationResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getUserEmailPendingValidation(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_user_has_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasBookings(options?: any): CancelablePromise<UserHasBookingResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getUserHasBookings(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_user_has_collective_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasCollectiveBookings(options?: any): CancelablePromise<UserHasBookingResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getUserHasCollectiveBookings(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenue(venue_id: number, options?: any): CancelablePromise<GetVenueResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenue(venue_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venue_stats_dashboard_url <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueStatsDashboardUrl(venue_id: number, options?: any): CancelablePromise<OffererStatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenueStatsDashboardUrl(venue_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venue_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueTypes(options?: any): CancelablePromise<VenueTypeListResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenueTypes(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venues <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [activeOfferersOnly] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenues(validated?: boolean, activeOfferersOnly?: boolean, offererId?: number, options?: any): CancelablePromise<GetVenueListResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenues(validated, activeOfferersOnly, offererId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venues_educational_statuses <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesEducationalStatuses(options?: any): CancelablePromise<VenuesEducationalStatusesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenuesEducationalStatuses(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venues_of_offerer_from_siret <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesOfOffererFromSiret(siret: string, options?: any): CancelablePromise<GetVenuesOfOffererFromSiretResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenuesOfOffererFromSiret(siret, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary has_invoice <GET>
     * @param {number} offererId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    hasInvoice(offererId: number, options?: any): CancelablePromise<HasInvoiceResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).hasInvoice(offererId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary invite_member <POST>
     * @param {number} offerer_id 
     * @param {InviteMemberQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    inviteMember(offerer_id: number, body?: InviteMemberQueryModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).inviteMember(offerer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary link_venue_to_bank_account <PATCH>
     * @param {number} offerer_id 
     * @param {number} bank_account_id 
     * @param {LinkVenueToBankAccountBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToBankAccount(offerer_id: number, bank_account_id: number, body?: LinkVenueToBankAccountBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).linkVenueToBankAccount(offerer_id, bank_account_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary link_venue_to_pricing_point <POST>
     * @param {number} venue_id 
     * @param {LinkVenueToPricingPointBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToPricingPoint(venue_id: number, body?: LinkVenueToPricingPointBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).linkVenueToPricingPoint(venue_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_educational_domains <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalDomains(options?: any): CancelablePromise<EducationalDomainsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listEducationalDomains(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_educational_offerers <GET>
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalOfferers(offerer_id?: number, options?: any): CancelablePromise<GetEducationalOfferersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listEducationalOfferers(offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_features <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listFeatures(options?: any): CancelablePromise<ListFeatureResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listFeatures(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_offerers_names <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [validated_for_user] 
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOfferersNames(validated?: boolean, validated_for_user?: boolean, offerer_id?: number, options?: any): CancelablePromise<GetOfferersNamesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listOfferersNames(validated, validated_for_user, offerer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status1} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType1} [collectiveOfferType] 
     * @param {number} [offererAddressId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOffers(nameOrIsbn?: string, offererId?: number, status?: Status1, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType1, offererAddressId?: number, options?: any): CancelablePromise<ListOffersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, offererAddressId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary list_venue_providers <GET>
     * @param {number} venueId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listVenueProviders(venueId: number, options?: any): CancelablePromise<ListVenueProviderResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).listVenueProviders(venueId, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_all_offers_active_status <PATCH>
     * @param {PatchAllOffersActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchAllOffersActiveStatus(body?: PatchAllOffersActiveStatusBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchAllOffersActiveStatus(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offer_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferPublication(offer_id: number, options?: any): CancelablePromise<GetCollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOfferPublication(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offer_template_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferTemplatePublication(offer_id: number, options?: any): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOfferTemplatePublication(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offers_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOffersActiveStatus(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offers_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOffersArchive(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offers_educational_institution <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferEducationalInstitution} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersEducationalInstitution(offer_id: number, body?: PatchCollectiveOfferEducationalInstitution, options?: any): CancelablePromise<GetCollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOffersEducationalInstitution(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offers_template_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOffersTemplateActiveStatus(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_collective_offers_template_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchCollectiveOffersTemplateArchive(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_draft_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchDraftOffer(offer_id: number, body?: PatchDraftOfferBodyModel, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchDraftOffer(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffer(offer_id: number, body?: PatchOfferBodyModel, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchOffer(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_offers_active_status <PATCH>
     * @param {PatchOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffersActiveStatus(body?: PatchOfferActiveStatusBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchOffersActiveStatus(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_pro_user_rgs_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchProUserRgsSeen(options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchProUserRgsSeen(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_publish_offer <PATCH>
     * @param {PatchOfferPublishBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchPublishOffer(body?: PatchOfferPublishBodyModel, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchPublishOffer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_user_identity <PATCH>
     * @param {UserIdentityBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserIdentity(body?: UserIdentityBodyModel, options?: any): CancelablePromise<UserIdentityResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchUserIdentity(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_user_phone <PATCH>
     * @param {UserPhoneBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserPhone(body?: UserPhoneBodyModel, options?: any): CancelablePromise<UserPhoneResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchUserPhone(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_user_tuto_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserTutoSeen(options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchUserTutoSeen(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary patch_validate_email <PATCH>
     * @param {ChangeProEmailBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchValidateEmail(body?: ChangeProEmailBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).patchValidateEmail(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_change_password <POST>
     * @param {ChangePasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postChangePassword(body?: ChangePasswordBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postChangePassword(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_create_venue <POST>
     * @param {PostVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCreateVenue(body?: PostVenueBodyModel, options?: any): CancelablePromise<VenueResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postCreateVenue(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_draft_offer <POST>
     * @param {PostDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postDraftOffer(body?: PostDraftOfferBodyModel, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postDraftOffer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_new_password <POST>
     * @param {NewPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postNewPassword(body?: NewPasswordBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postNewPassword(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_offer <POST>
     * @param {PostOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postOffer(body?: PostOfferBodyModel, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postOffer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_price_categories <POST>
     * @param {number} offer_id 
     * @param {PriceCategoryBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postPriceCategories(offer_id: number, body?: PriceCategoryBody, options?: any): CancelablePromise<GetIndividualOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postPriceCategories(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_pro_flags <POST>
     * @param {ProFlagsQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postProFlags(body?: ProFlagsQueryModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postProFlags(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_user_email <POST>
     * @param {UserResetEmailBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postUserEmail(body?: UserResetEmailBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postUserEmail(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary reset_password <POST>
     * @param {ResetPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    resetPassword(body?: ResetPasswordBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).resetPassword(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary save_new_onboarding_data <POST>
     * @param {SaveNewOnboardingDataQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveNewOnboardingData(body?: SaveNewOnboardingDataQueryModel, options?: any): CancelablePromise<PostOffererResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).saveNewOnboardingData(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary signin <POST>
     * @param {LoginUserBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signin(body?: LoginUserBodyModel, options?: any): CancelablePromise<SharedLoginUserResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).signin(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary signout <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signout(options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).signout(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary signup_pro_V2 <POST>
     * @param {ProUserCreationBodyV2Model} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signupProV2(body?: ProUserCreationBodyV2Model, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).signupProV2(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary submit_user_review <POST>
     * @param {SubmitReviewRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    submitUserReview(body?: SubmitReviewRequestModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).submitUserReview(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary update_venue_provider <PUT>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateVenueProvider(body?: PostVenueProviderBody, options?: any): CancelablePromise<VenueProviderResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).updateVenueProvider(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary upsert_stocks <POST>
     * @param {StocksUpsertBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    upsertStocks(body?: StocksUpsertBodyModel, options?: any): CancelablePromise<StocksResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).upsertStocks(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary validate_user <PATCH>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    validateUser(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).validateUser(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
  }
}

/**
 * DefaultApi - factory interface
 * @export
 */
export const DefaultApiFactory = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary attach_offer_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any) {
      return DefaultApiFp(configuration).attachOfferImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
    },
    /**
     * 
     * @summary attach_offer_template_image <POST>
     * @param {number} offer_id 
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    attachOfferTemplateImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any) {
      return DefaultApiFp(configuration).attachOfferTemplateImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
    },
    /**
     * 
     * @summary cancel_collective_offer_booking <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cancelCollectiveOfferBooking(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).cancelCollectiveOfferBooking(offer_id, options)
    },
    /**
     * 
     * @summary check_activation_token_exists <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    checkActivationTokenExists(token: string, options?: any) {
      return DefaultApiFp(configuration).checkActivationTokenExists(token, options)
    },
    /**
     * 
     * @summary connect_as <GET>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    connectAs(token: string, options?: any) {
      return DefaultApiFp(configuration).connectAs(token, options)
    },
    /**
     * 
     * @summary cookies_consent <POST>
     * @param {CookieConsentRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    cookiesConsent(body?: CookieConsentRequest, options?: any) {
      return DefaultApiFp(configuration).cookiesConsent(body, options)
    },
    /**
     * 
     * @summary create_collective_offer <POST>
     * @param {PostCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOffer(body?: PostCollectiveOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).createCollectiveOffer(body, options)
    },
    /**
     * 
     * @summary create_collective_offer_template <POST>
     * @param {PostCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplate(body?: PostCollectiveOfferTemplateBodyModel, options?: any) {
      return DefaultApiFp(configuration).createCollectiveOfferTemplate(body, options)
    },
    /**
     * 
     * @summary create_collective_offer_template_from_collective_offer <POST>
     * @param {number} offer_id 
     * @param {CollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveOfferTemplateFromCollectiveOffer(offer_id: number, body?: CollectiveOfferTemplateBodyModel, options?: any) {
      return DefaultApiFp(configuration).createCollectiveOfferTemplateFromCollectiveOffer(offer_id, body, options)
    },
    /**
     * 
     * @summary create_collective_stock <POST>
     * @param {CollectiveStockCreationBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveStock(body?: CollectiveStockCreationBodyModel, options?: any) {
      return DefaultApiFp(configuration).createCollectiveStock(body, options)
    },
    /**
     * 
     * @summary create_offerer <POST>
     * @param {CreateOffererQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOfferer(body?: CreateOffererQueryModel, options?: any) {
      return DefaultApiFp(configuration).createOfferer(body, options)
    },
    /**
     * 
     * @summary create_offerer_address <POST>
     * @param {number} offerer_id 
     * @param {OffererAddressRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createOffererAddress(offerer_id: number, body?: OffererAddressRequestModel, options?: any) {
      return DefaultApiFp(configuration).createOffererAddress(offerer_id, body, options)
    },
    /**
     * 
     * @summary create_thumbnail <POST>
     * @param {string} [credit] 
     * @param {number} [croppingRectHeight] 
     * @param {number} [croppingRectWidth] 
     * @param {number} [croppingRectX] 
     * @param {number} [croppingRectY] 
     * @param {number} [offerId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createThumbnail(credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, offerId?: number, options?: any) {
      return DefaultApiFp(configuration).createThumbnail(credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, offerId, options)
    },
    /**
     * 
     * @summary create_venue_provider <POST>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createVenueProvider(body?: PostVenueProviderBody, options?: any) {
      return DefaultApiFp(configuration).createVenueProvider(body, options)
    },
    /**
     * 
     * @summary delete_all_filtered_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteFilteredStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteAllFilteredStocks(offer_id: number, body?: DeleteFilteredStockListBody, options?: any) {
      return DefaultApiFp(configuration).deleteAllFilteredStocks(offer_id, body, options)
    },
    /**
     * 
     * @summary delete_api_key <DELETE>
     * @param {string} api_key_prefix 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteApiKey(api_key_prefix: string, options?: any) {
      return DefaultApiFp(configuration).deleteApiKey(api_key_prefix, options)
    },
    /**
     * 
     * @summary delete_draft_offers <POST>
     * @param {DeleteOfferRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteDraftOffers(body?: DeleteOfferRequestBody, options?: any) {
      return DefaultApiFp(configuration).deleteDraftOffers(body, options)
    },
    /**
     * 
     * @summary delete_offer_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferImage(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteOfferImage(offer_id, options)
    },
    /**
     * 
     * @summary delete_offer_template_image <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteOfferTemplateImage(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteOfferTemplateImage(offer_id, options)
    },
    /**
     * 
     * @summary delete_price_category <DELETE>
     * @param {number} offer_id 
     * @param {number} price_category_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deletePriceCategory(offer_id: number, price_category_id: number, options?: any) {
      return DefaultApiFp(configuration).deletePriceCategory(offer_id, price_category_id, options)
    },
    /**
     * 
     * @summary delete_stock <DELETE>
     * @param {number} stock_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStock(stock_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteStock(stock_id, options)
    },
    /**
     * 
     * @summary delete_stocks <POST>
     * @param {number} offer_id 
     * @param {DeleteStockListBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteStocks(offer_id: number, body?: DeleteStockListBody, options?: any) {
      return DefaultApiFp(configuration).deleteStocks(offer_id, body, options)
    },
    /**
     * 
     * @summary delete_thumbnail <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteThumbnail(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteThumbnail(offer_id, options)
    },
    /**
     * 
     * @summary delete_venue_banner <DELETE>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueBanner(venue_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteVenueBanner(venue_id, options)
    },
    /**
     * 
     * @summary delete_venue_provider <DELETE>
     * @param {number} venue_provider_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteVenueProvider(venue_provider_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteVenueProvider(venue_provider_id, options)
    },
    /**
     * 
     * @summary duplicate_collective_offer <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    duplicateCollectiveOffer(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).duplicateCollectiveOffer(offer_id, options)
    },
    /**
     * 
     * @summary edit_collective_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOffer(offer_id: number, body?: PatchCollectiveOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).editCollectiveOffer(offer_id, body, options)
    },
    /**
     * 
     * @summary edit_collective_offer_template <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferTemplateBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveOfferTemplate(offer_id: number, body?: PatchCollectiveOfferTemplateBodyModel, options?: any) {
      return DefaultApiFp(configuration).editCollectiveOfferTemplate(offer_id, body, options)
    },
    /**
     * 
     * @summary edit_collective_stock <PATCH>
     * @param {number} collective_stock_id 
     * @param {CollectiveStockEditionBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editCollectiveStock(collective_stock_id: number, body?: CollectiveStockEditionBodyModel, options?: any) {
      return DefaultApiFp(configuration).editCollectiveStock(collective_stock_id, body, options)
    },
    /**
     * 
     * @summary edit_venue <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenue(venue_id: number, body?: EditVenueBodyModel, options?: any) {
      return DefaultApiFp(configuration).editVenue(venue_id, body, options)
    },
    /**
     * 
     * @summary edit_venue_collective_data <PATCH>
     * @param {number} venue_id 
     * @param {EditVenueCollectiveDataBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    editVenueCollectiveData(venue_id: number, body?: EditVenueCollectiveDataBodyModel, options?: any) {
      return DefaultApiFp(configuration).editVenueCollectiveData(venue_id, body, options)
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_csv <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsCsv(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any) {
      return DefaultApiFp(configuration).exportBookingsForOfferAsCsv(offer_id, status, event_date, options)
    },
    /**
     * 
     * @summary export_bookings_for_offer_as_excel <GET>
     * @param {number} offer_id 
     * @param {BookingsExportStatusFilter} status 
     * @param {string} event_date 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    exportBookingsForOfferAsExcel(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any) {
      return DefaultApiFp(configuration).exportBookingsForOfferAsExcel(offer_id, status, event_date, options)
    },
    /**
     * 
     * @summary fetch_venue_labels <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    fetchVenueLabels(options?: any) {
      return DefaultApiFp(configuration).fetchVenueLabels(options)
    },
    /**
     * 
     * @summary get_autocomplete_educational_redactors_for_uai <GET>
     * @param {string} uai 
     * @param {string} candidate 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAutocompleteEducationalRedactorsForUai(uai: string, candidate: string, options?: any) {
      return DefaultApiFp(configuration).getAutocompleteEducationalRedactorsForUai(uai, candidate, options)
    },
    /**
     * 
     * @summary get_bank_accounts <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBankAccounts(options?: any) {
      return DefaultApiFp(configuration).getBankAccounts(options)
    },
    /**
     * 
     * @summary get_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsCsv(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType, options?: any) {
      return DefaultApiFp(configuration).getBookingsCsv(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
    },
    /**
     * 
     * @summary get_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter1} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType1} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsExcel(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter1, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType1, options?: any) {
      return DefaultApiFp(configuration).getBookingsExcel(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
    },
    /**
     * 
     * @summary get_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {number} [offerId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter2} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {number} [offererAddressId] 
     * @param {ExportType2} [exportType] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingsPro(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter2, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType2, options?: any) {
      return DefaultApiFp(configuration).getBookingsPro(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
    },
    /**
     * 
     * @summary get_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCategories(options?: any) {
      return DefaultApiFp(configuration).getCategories(options)
    },
    /**
     * 
     * @summary get_collective_booking_by_id <GET>
     * @param {number} booking_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingById(booking_id: number, options?: any) {
      return DefaultApiFp(configuration).getCollectiveBookingById(booking_id, options)
    },
    /**
     * 
     * @summary get_collective_bookings_csv <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter3} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsCsv(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter3, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
      return DefaultApiFp(configuration).getCollectiveBookingsCsv(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
    },
    /**
     * 
     * @summary get_collective_bookings_excel <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter4} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsExcel(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter4, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
      return DefaultApiFp(configuration).getCollectiveBookingsExcel(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
    },
    /**
     * 
     * @summary get_collective_bookings_pro <GET>
     * @param {number} [page] 
     * @param {number} [venueId] 
     * @param {string} [eventDate] 
     * @param {BookingStatusFilter5} [bookingStatusFilter] 
     * @param {string} [bookingPeriodBeginningDate] 
     * @param {string} [bookingPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveBookingsPro(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter5, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
      return DefaultApiFp(configuration).getCollectiveBookingsPro(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
    },
    /**
     * 
     * @summary get_collective_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffer(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).getCollectiveOffer(offer_id, options)
    },
    /**
     * 
     * @summary get_collective_offer_request <GET>
     * @param {number} request_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferRequest(request_id: number, options?: any) {
      return DefaultApiFp(configuration).getCollectiveOfferRequest(request_id, options)
    },
    /**
     * 
     * @summary get_collective_offer_template <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplate(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).getCollectiveOfferTemplate(offer_id, options)
    },
    /**
     * 
     * @summary get_collective_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType} [collectiveOfferType] 
     * @param {Format} [format] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffers(nameOrIsbn?: string, offererId?: number, status?: Status, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType, format?: Format, options?: any) {
      return DefaultApiFp(configuration).getCollectiveOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, format, options)
    },
    /**
     * 
     * @summary get_combined_invoices <GET>
     * @param {Array<string>} invoiceReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCombinedInvoices(invoiceReferences: Array<string>, options?: any) {
      return DefaultApiFp(configuration).getCombinedInvoices(invoiceReferences, options)
    },
    /**
     * 
     * @summary get_educational_institutions <GET>
     * @param {number} [perPageLimit] 
     * @param {number} [page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutions(perPageLimit?: number, page?: number, options?: any) {
      return DefaultApiFp(configuration).getEducationalInstitutions(perPageLimit, page, options)
    },
    /**
     * 
     * @summary get_educational_partners <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalPartners(options?: any) {
      return DefaultApiFp(configuration).getEducationalPartners(options)
    },
    /**
     * 
     * @summary get_invoices_v2 <GET>
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {number} [bankAccountId] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getInvoicesV2(periodBeginningDate?: string, periodEndingDate?: string, bankAccountId?: number, offererId?: number, options?: any) {
      return DefaultApiFp(configuration).getInvoicesV2(periodBeginningDate, periodEndingDate, bankAccountId, offererId, options)
    },
    /**
     * 
     * @summary get_music_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getMusicTypes(options?: any) {
      return DefaultApiFp(configuration).getMusicTypes(options)
    },
    /**
     * 
     * @summary get_national_programs <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNationalPrograms(options?: any) {
      return DefaultApiFp(configuration).getNationalPrograms(options)
    },
    /**
     * 
     * @summary get_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffer(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffer(offer_id, options)
    },
    /**
     * 
     * @summary get_offer_price_categories_and_schedules_by_dates <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferPriceCategoriesAndSchedulesByDates(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOfferPriceCategoriesAndSchedulesByDates(offer_id, options)
    },
    /**
     * 
     * @summary get_offerer <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOfferer(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOfferer(offerer_id, options)
    },
    /**
     * 
     * @summary get_offerer_addresses <GET>
     * @param {number} offerer_id 
     * @param {boolean} [onlyWithOffers] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererAddresses(offerer_id: number, onlyWithOffers?: boolean, options?: any) {
      return DefaultApiFp(configuration).getOffererAddresses(offerer_id, onlyWithOffers, options)
    },
    /**
     * 
     * @summary get_offerer_bank_accounts_and_attached_venues <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererBankAccountsAndAttachedVenues(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffererBankAccountsAndAttachedVenues(offerer_id, options)
    },
    /**
     * 
     * @summary get_offerer_members <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererMembers(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffererMembers(offerer_id, options)
    },
    /**
     * 
     * @summary get_offerer_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStats(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffererStats(offerer_id, options)
    },
    /**
     * 
     * @summary get_offerer_stats_dashboard_url <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererStatsDashboardUrl(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffererStatsDashboardUrl(offerer_id, options)
    },
    /**
     * 
     * @summary get_offerer_v2_stats <GET>
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getOffererV2Stats(offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getOffererV2Stats(offerer_id, options)
    },
    /**
     * 
     * @summary get_product_by_ean <GET>
     * @param {string} ean 
     * @param {number} offerer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProductByEan(ean: string, offerer_id: number, options?: any) {
      return DefaultApiFp(configuration).getProductByEan(ean, offerer_id, options)
    },
    /**
     * 
     * @summary get_profile <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProfile(options?: any) {
      return DefaultApiFp(configuration).getProfile(options)
    },
    /**
     * 
     * @summary get_providers_by_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getProvidersByVenue(venue_id: number, options?: any) {
      return DefaultApiFp(configuration).getProvidersByVenue(venue_id, options)
    },
    /**
     * 
     * @summary get_reimbursements_csv <GET>
     * @param {number} offererId 
     * @param {number} [bankAccountId] 
     * @param {string} [reimbursementPeriodBeginningDate] 
     * @param {string} [reimbursementPeriodEndingDate] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsv(offererId: number, bankAccountId?: number, reimbursementPeriodBeginningDate?: string, reimbursementPeriodEndingDate?: string, options?: any) {
      return DefaultApiFp(configuration).getReimbursementsCsv(offererId, bankAccountId, reimbursementPeriodBeginningDate, reimbursementPeriodEndingDate, options)
    },
    /**
     * 
     * @summary get_reimbursements_csv_v2 <GET>
     * @param {Array<string>} invoicesReferences 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getReimbursementsCsvV2(invoicesReferences: Array<string>, options?: any) {
      return DefaultApiFp(configuration).getReimbursementsCsvV2(invoicesReferences, options)
    },
    /**
     * 
     * @summary get_siren_info <GET>
     * @param {string} siren 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSirenInfo(siren: string, options?: any) {
      return DefaultApiFp(configuration).getSirenInfo(siren, options)
    },
    /**
     * 
     * @summary get_siret_info <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSiretInfo(siret: string, options?: any) {
      return DefaultApiFp(configuration).getSiretInfo(siret, options)
    },
    /**
     * 
     * @summary get_statistics <GET>
     * @param {VenueIds} [venue_ids] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStatistics(venue_ids?: VenueIds, options?: any) {
      return DefaultApiFp(configuration).getStatistics(venue_ids, options)
    },
    /**
     * 
     * @summary get_stocks <GET>
     * @param {number} offer_id 
     * @param {string} [date] 
     * @param {string} [time] 
     * @param {number} [price_category_id] 
     * @param {OrderBy} [order_by] 
     * @param {boolean} [order_by_desc] 
     * @param {number} [page] 
     * @param {number} [stocks_limit_per_page] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocks(offer_id: number, date?: string, time?: string, price_category_id?: number, order_by?: OrderBy, order_by_desc?: boolean, page?: number, stocks_limit_per_page?: number, options?: any) {
      return DefaultApiFp(configuration).getStocks(offer_id, date, time, price_category_id, order_by, order_by_desc, page, stocks_limit_per_page, options)
    },
    /**
     * 
     * @summary get_stocks_stats <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getStocksStats(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).getStocksStats(offer_id, options)
    },
    /**
     * 
     * @summary get_suggested_subcategories <GET>
     * @param {string} offer_name 
     * @param {string} [offer_description] 
     * @param {number} [venue_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getSuggestedSubcategories(offer_name: string, offer_description?: string, venue_id?: number, options?: any) {
      return DefaultApiFp(configuration).getSuggestedSubcategories(offer_name, offer_description, venue_id, options)
    },
    /**
     * 
     * @summary get_user_email_pending_validation <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserEmailPendingValidation(options?: any) {
      return DefaultApiFp(configuration).getUserEmailPendingValidation(options)
    },
    /**
     * 
     * @summary get_user_has_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasBookings(options?: any) {
      return DefaultApiFp(configuration).getUserHasBookings(options)
    },
    /**
     * 
     * @summary get_user_has_collective_bookings <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getUserHasCollectiveBookings(options?: any) {
      return DefaultApiFp(configuration).getUserHasCollectiveBookings(options)
    },
    /**
     * 
     * @summary get_venue <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenue(venue_id: number, options?: any) {
      return DefaultApiFp(configuration).getVenue(venue_id, options)
    },
    /**
     * 
     * @summary get_venue_stats_dashboard_url <GET>
     * @param {number} venue_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueStatsDashboardUrl(venue_id: number, options?: any) {
      return DefaultApiFp(configuration).getVenueStatsDashboardUrl(venue_id, options)
    },
    /**
     * 
     * @summary get_venue_types <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueTypes(options?: any) {
      return DefaultApiFp(configuration).getVenueTypes(options)
    },
    /**
     * 
     * @summary get_venues <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [activeOfferersOnly] 
     * @param {number} [offererId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenues(validated?: boolean, activeOfferersOnly?: boolean, offererId?: number, options?: any) {
      return DefaultApiFp(configuration).getVenues(validated, activeOfferersOnly, offererId, options)
    },
    /**
     * 
     * @summary get_venues_educational_statuses <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesEducationalStatuses(options?: any) {
      return DefaultApiFp(configuration).getVenuesEducationalStatuses(options)
    },
    /**
     * 
     * @summary get_venues_of_offerer_from_siret <GET>
     * @param {string} siret 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenuesOfOffererFromSiret(siret: string, options?: any) {
      return DefaultApiFp(configuration).getVenuesOfOffererFromSiret(siret, options)
    },
    /**
     * 
     * @summary has_invoice <GET>
     * @param {number} offererId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    hasInvoice(offererId: number, options?: any) {
      return DefaultApiFp(configuration).hasInvoice(offererId, options)
    },
    /**
     * 
     * @summary invite_member <POST>
     * @param {number} offerer_id 
     * @param {InviteMemberQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    inviteMember(offerer_id: number, body?: InviteMemberQueryModel, options?: any) {
      return DefaultApiFp(configuration).inviteMember(offerer_id, body, options)
    },
    /**
     * 
     * @summary link_venue_to_bank_account <PATCH>
     * @param {number} offerer_id 
     * @param {number} bank_account_id 
     * @param {LinkVenueToBankAccountBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToBankAccount(offerer_id: number, bank_account_id: number, body?: LinkVenueToBankAccountBodyModel, options?: any) {
      return DefaultApiFp(configuration).linkVenueToBankAccount(offerer_id, bank_account_id, body, options)
    },
    /**
     * 
     * @summary link_venue_to_pricing_point <POST>
     * @param {number} venue_id 
     * @param {LinkVenueToPricingPointBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    linkVenueToPricingPoint(venue_id: number, body?: LinkVenueToPricingPointBodyModel, options?: any) {
      return DefaultApiFp(configuration).linkVenueToPricingPoint(venue_id, body, options)
    },
    /**
     * 
     * @summary list_educational_domains <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalDomains(options?: any) {
      return DefaultApiFp(configuration).listEducationalDomains(options)
    },
    /**
     * 
     * @summary list_educational_offerers <GET>
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listEducationalOfferers(offerer_id?: number, options?: any) {
      return DefaultApiFp(configuration).listEducationalOfferers(offerer_id, options)
    },
    /**
     * 
     * @summary list_features <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listFeatures(options?: any) {
      return DefaultApiFp(configuration).listFeatures(options)
    },
    /**
     * 
     * @summary list_offerers_names <GET>
     * @param {boolean} [validated] 
     * @param {boolean} [validated_for_user] 
     * @param {number} [offerer_id] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOfferersNames(validated?: boolean, validated_for_user?: boolean, offerer_id?: number, options?: any) {
      return DefaultApiFp(configuration).listOfferersNames(validated, validated_for_user, offerer_id, options)
    },
    /**
     * 
     * @summary list_offers <GET>
     * @param {string} [nameOrIsbn] 
     * @param {number} [offererId] 
     * @param {Status1} [status] 
     * @param {number} [venueId] 
     * @param {string} [categoryId] 
     * @param {string} [creationMode] 
     * @param {string} [periodBeginningDate] 
     * @param {string} [periodEndingDate] 
     * @param {CollectiveOfferType1} [collectiveOfferType] 
     * @param {number} [offererAddressId] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listOffers(nameOrIsbn?: string, offererId?: number, status?: Status1, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType1, offererAddressId?: number, options?: any) {
      return DefaultApiFp(configuration).listOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, offererAddressId, options)
    },
    /**
     * 
     * @summary list_venue_providers <GET>
     * @param {number} venueId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    listVenueProviders(venueId: number, options?: any) {
      return DefaultApiFp(configuration).listVenueProviders(venueId, options)
    },
    /**
     * 
     * @summary patch_all_offers_active_status <PATCH>
     * @param {PatchAllOffersActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchAllOffersActiveStatus(body?: PatchAllOffersActiveStatusBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchAllOffersActiveStatus(body, options)
    },
    /**
     * 
     * @summary patch_collective_offer_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferPublication(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOfferPublication(offer_id, options)
    },
    /**
     * 
     * @summary patch_collective_offer_template_publication <PATCH>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOfferTemplatePublication(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOfferTemplatePublication(offer_id, options)
    },
    /**
     * 
     * @summary patch_collective_offers_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOffersActiveStatus(body, options)
    },
    /**
     * 
     * @summary patch_collective_offers_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOffersArchive(body, options)
    },
    /**
     * 
     * @summary patch_collective_offers_educational_institution <PATCH>
     * @param {number} offer_id 
     * @param {PatchCollectiveOfferEducationalInstitution} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersEducationalInstitution(offer_id: number, body?: PatchCollectiveOfferEducationalInstitution, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOffersEducationalInstitution(offer_id, body, options)
    },
    /**
     * 
     * @summary patch_collective_offers_template_active_status <PATCH>
     * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOffersTemplateActiveStatus(body, options)
    },
    /**
     * 
     * @summary patch_collective_offers_template_archive <PATCH>
     * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCollectiveOffersTemplateArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchCollectiveOffersTemplateArchive(body, options)
    },
    /**
     * 
     * @summary patch_draft_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchDraftOffer(offer_id: number, body?: PatchDraftOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchDraftOffer(offer_id, body, options)
    },
    /**
     * 
     * @summary patch_offer <PATCH>
     * @param {number} offer_id 
     * @param {PatchOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffer(offer_id: number, body?: PatchOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchOffer(offer_id, body, options)
    },
    /**
     * 
     * @summary patch_offers_active_status <PATCH>
     * @param {PatchOfferActiveStatusBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchOffersActiveStatus(body?: PatchOfferActiveStatusBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchOffersActiveStatus(body, options)
    },
    /**
     * 
     * @summary patch_pro_user_rgs_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchProUserRgsSeen(options?: any) {
      return DefaultApiFp(configuration).patchProUserRgsSeen(options)
    },
    /**
     * 
     * @summary patch_publish_offer <PATCH>
     * @param {PatchOfferPublishBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchPublishOffer(body?: PatchOfferPublishBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchPublishOffer(body, options)
    },
    /**
     * 
     * @summary patch_user_identity <PATCH>
     * @param {UserIdentityBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserIdentity(body?: UserIdentityBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchUserIdentity(body, options)
    },
    /**
     * 
     * @summary patch_user_phone <PATCH>
     * @param {UserPhoneBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserPhone(body?: UserPhoneBodyModel, options?: any) {
      return DefaultApiFp(configuration).patchUserPhone(body, options)
    },
    /**
     * 
     * @summary patch_user_tuto_seen <PATCH>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchUserTutoSeen(options?: any) {
      return DefaultApiFp(configuration).patchUserTutoSeen(options)
    },
    /**
     * 
     * @summary patch_validate_email <PATCH>
     * @param {ChangeProEmailBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchValidateEmail(body?: ChangeProEmailBody, options?: any) {
      return DefaultApiFp(configuration).patchValidateEmail(body, options)
    },
    /**
     * 
     * @summary post_change_password <POST>
     * @param {ChangePasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postChangePassword(body?: ChangePasswordBodyModel, options?: any) {
      return DefaultApiFp(configuration).postChangePassword(body, options)
    },
    /**
     * 
     * @summary post_create_venue <POST>
     * @param {PostVenueBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCreateVenue(body?: PostVenueBodyModel, options?: any) {
      return DefaultApiFp(configuration).postCreateVenue(body, options)
    },
    /**
     * 
     * @summary post_draft_offer <POST>
     * @param {PostDraftOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postDraftOffer(body?: PostDraftOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).postDraftOffer(body, options)
    },
    /**
     * 
     * @summary post_new_password <POST>
     * @param {NewPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postNewPassword(body?: NewPasswordBodyModel, options?: any) {
      return DefaultApiFp(configuration).postNewPassword(body, options)
    },
    /**
     * 
     * @summary post_offer <POST>
     * @param {PostOfferBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postOffer(body?: PostOfferBodyModel, options?: any) {
      return DefaultApiFp(configuration).postOffer(body, options)
    },
    /**
     * 
     * @summary post_price_categories <POST>
     * @param {number} offer_id 
     * @param {PriceCategoryBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postPriceCategories(offer_id: number, body?: PriceCategoryBody, options?: any) {
      return DefaultApiFp(configuration).postPriceCategories(offer_id, body, options)
    },
    /**
     * 
     * @summary post_pro_flags <POST>
     * @param {ProFlagsQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postProFlags(body?: ProFlagsQueryModel, options?: any) {
      return DefaultApiFp(configuration).postProFlags(body, options)
    },
    /**
     * 
     * @summary post_user_email <POST>
     * @param {UserResetEmailBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postUserEmail(body?: UserResetEmailBodyModel, options?: any) {
      return DefaultApiFp(configuration).postUserEmail(body, options)
    },
    /**
     * 
     * @summary reset_password <POST>
     * @param {ResetPasswordBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    resetPassword(body?: ResetPasswordBodyModel, options?: any) {
      return DefaultApiFp(configuration).resetPassword(body, options)
    },
    /**
     * 
     * @summary save_new_onboarding_data <POST>
     * @param {SaveNewOnboardingDataQueryModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveNewOnboardingData(body?: SaveNewOnboardingDataQueryModel, options?: any) {
      return DefaultApiFp(configuration).saveNewOnboardingData(body, options)
    },
    /**
     * 
     * @summary signin <POST>
     * @param {LoginUserBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signin(body?: LoginUserBodyModel, options?: any) {
      return DefaultApiFp(configuration).signin(body, options)
    },
    /**
     * 
     * @summary signout <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signout(options?: any) {
      return DefaultApiFp(configuration).signout(options)
    },
    /**
     * 
     * @summary signup_pro_V2 <POST>
     * @param {ProUserCreationBodyV2Model} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    signupProV2(body?: ProUserCreationBodyV2Model, options?: any) {
      return DefaultApiFp(configuration).signupProV2(body, options)
    },
    /**
     * 
     * @summary submit_user_review <POST>
     * @param {SubmitReviewRequestModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    submitUserReview(body?: SubmitReviewRequestModel, options?: any) {
      return DefaultApiFp(configuration).submitUserReview(body, options)
    },
    /**
     * 
     * @summary update_venue_provider <PUT>
     * @param {PostVenueProviderBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateVenueProvider(body?: PostVenueProviderBody, options?: any) {
      return DefaultApiFp(configuration).updateVenueProvider(body, options)
    },
    /**
     * 
     * @summary upsert_stocks <POST>
     * @param {StocksUpsertBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    upsertStocks(body?: StocksUpsertBodyModel, options?: any) {
      return DefaultApiFp(configuration).upsertStocks(body, options)
    },
    /**
     * 
     * @summary validate_user <PATCH>
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    validateUser(token: string, options?: any) {
      return DefaultApiFp(configuration).validateUser(token, options)
    },
  }
}

/**
 * DefaultApi - object-oriented interface
 * @export
 * @class DefaultApi
 * @extends {BaseAPI}
 */
export class DefaultApi extends BaseAPI {
  /**
   * 
   * @summary attach_offer_image <POST>
   * @param {number} offer_id 
   * @param {string} [credit] 
   * @param {number} [croppingRectHeight] 
   * @param {number} [croppingRectWidth] 
   * @param {number} [croppingRectX] 
   * @param {number} [croppingRectY] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public attachOfferImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any) {
    return DefaultApiFp(this.configuration).attachOfferImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
  }

  /**
   * 
   * @summary attach_offer_template_image <POST>
   * @param {number} offer_id 
   * @param {string} [credit] 
   * @param {number} [croppingRectHeight] 
   * @param {number} [croppingRectWidth] 
   * @param {number} [croppingRectX] 
   * @param {number} [croppingRectY] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public attachOfferTemplateImage(offer_id: number, credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, options?: any) {
    return DefaultApiFp(this.configuration).attachOfferTemplateImage(offer_id, credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, options)
  }

  /**
   * 
   * @summary cancel_collective_offer_booking <PATCH>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public cancelCollectiveOfferBooking(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).cancelCollectiveOfferBooking(offer_id, options)
  }

  /**
   * 
   * @summary check_activation_token_exists <GET>
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public checkActivationTokenExists(token: string, options?: any) {
    return DefaultApiFp(this.configuration).checkActivationTokenExists(token, options)
  }

  /**
   * 
   * @summary connect_as <GET>
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public connectAs(token: string, options?: any) {
    return DefaultApiFp(this.configuration).connectAs(token, options)
  }

  /**
   * 
   * @summary cookies_consent <POST>
   * @param {CookieConsentRequest} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public cookiesConsent(body?: CookieConsentRequest, options?: any) {
    return DefaultApiFp(this.configuration).cookiesConsent(body, options)
  }

  /**
   * 
   * @summary create_collective_offer <POST>
   * @param {PostCollectiveOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createCollectiveOffer(body?: PostCollectiveOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).createCollectiveOffer(body, options)
  }

  /**
   * 
   * @summary create_collective_offer_template <POST>
   * @param {PostCollectiveOfferTemplateBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createCollectiveOfferTemplate(body?: PostCollectiveOfferTemplateBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).createCollectiveOfferTemplate(body, options)
  }

  /**
   * 
   * @summary create_collective_offer_template_from_collective_offer <POST>
   * @param {number} offer_id 
   * @param {CollectiveOfferTemplateBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createCollectiveOfferTemplateFromCollectiveOffer(offer_id: number, body?: CollectiveOfferTemplateBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).createCollectiveOfferTemplateFromCollectiveOffer(offer_id, body, options)
  }

  /**
   * 
   * @summary create_collective_stock <POST>
   * @param {CollectiveStockCreationBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createCollectiveStock(body?: CollectiveStockCreationBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).createCollectiveStock(body, options)
  }

  /**
   * 
   * @summary create_offerer <POST>
   * @param {CreateOffererQueryModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createOfferer(body?: CreateOffererQueryModel, options?: any) {
    return DefaultApiFp(this.configuration).createOfferer(body, options)
  }

  /**
   * 
   * @summary create_offerer_address <POST>
   * @param {number} offerer_id 
   * @param {OffererAddressRequestModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createOffererAddress(offerer_id: number, body?: OffererAddressRequestModel, options?: any) {
    return DefaultApiFp(this.configuration).createOffererAddress(offerer_id, body, options)
  }

  /**
   * 
   * @summary create_thumbnail <POST>
   * @param {string} [credit] 
   * @param {number} [croppingRectHeight] 
   * @param {number} [croppingRectWidth] 
   * @param {number} [croppingRectX] 
   * @param {number} [croppingRectY] 
   * @param {number} [offerId] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createThumbnail(credit?: string, croppingRectHeight?: number, croppingRectWidth?: number, croppingRectX?: number, croppingRectY?: number, offerId?: number, options?: any) {
    return DefaultApiFp(this.configuration).createThumbnail(credit, croppingRectHeight, croppingRectWidth, croppingRectX, croppingRectY, offerId, options)
  }

  /**
   * 
   * @summary create_venue_provider <POST>
   * @param {PostVenueProviderBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createVenueProvider(body?: PostVenueProviderBody, options?: any) {
    return DefaultApiFp(this.configuration).createVenueProvider(body, options)
  }

  /**
   * 
   * @summary delete_all_filtered_stocks <POST>
   * @param {number} offer_id 
   * @param {DeleteFilteredStockListBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteAllFilteredStocks(offer_id: number, body?: DeleteFilteredStockListBody, options?: any) {
    return DefaultApiFp(this.configuration).deleteAllFilteredStocks(offer_id, body, options)
  }

  /**
   * 
   * @summary delete_api_key <DELETE>
   * @param {string} api_key_prefix 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteApiKey(api_key_prefix: string, options?: any) {
    return DefaultApiFp(this.configuration).deleteApiKey(api_key_prefix, options)
  }

  /**
   * 
   * @summary delete_draft_offers <POST>
   * @param {DeleteOfferRequestBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteDraftOffers(body?: DeleteOfferRequestBody, options?: any) {
    return DefaultApiFp(this.configuration).deleteDraftOffers(body, options)
  }

  /**
   * 
   * @summary delete_offer_image <DELETE>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteOfferImage(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteOfferImage(offer_id, options)
  }

  /**
   * 
   * @summary delete_offer_template_image <DELETE>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteOfferTemplateImage(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteOfferTemplateImage(offer_id, options)
  }

  /**
   * 
   * @summary delete_price_category <DELETE>
   * @param {number} offer_id 
   * @param {number} price_category_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deletePriceCategory(offer_id: number, price_category_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deletePriceCategory(offer_id, price_category_id, options)
  }

  /**
   * 
   * @summary delete_stock <DELETE>
   * @param {number} stock_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteStock(stock_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteStock(stock_id, options)
  }

  /**
   * 
   * @summary delete_stocks <POST>
   * @param {number} offer_id 
   * @param {DeleteStockListBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteStocks(offer_id: number, body?: DeleteStockListBody, options?: any) {
    return DefaultApiFp(this.configuration).deleteStocks(offer_id, body, options)
  }

  /**
   * 
   * @summary delete_thumbnail <DELETE>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteThumbnail(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteThumbnail(offer_id, options)
  }

  /**
   * 
   * @summary delete_venue_banner <DELETE>
   * @param {number} venue_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteVenueBanner(venue_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteVenueBanner(venue_id, options)
  }

  /**
   * 
   * @summary delete_venue_provider <DELETE>
   * @param {number} venue_provider_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteVenueProvider(venue_provider_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteVenueProvider(venue_provider_id, options)
  }

  /**
   * 
   * @summary duplicate_collective_offer <POST>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public duplicateCollectiveOffer(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).duplicateCollectiveOffer(offer_id, options)
  }

  /**
   * 
   * @summary edit_collective_offer <PATCH>
   * @param {number} offer_id 
   * @param {PatchCollectiveOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public editCollectiveOffer(offer_id: number, body?: PatchCollectiveOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).editCollectiveOffer(offer_id, body, options)
  }

  /**
   * 
   * @summary edit_collective_offer_template <PATCH>
   * @param {number} offer_id 
   * @param {PatchCollectiveOfferTemplateBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public editCollectiveOfferTemplate(offer_id: number, body?: PatchCollectiveOfferTemplateBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).editCollectiveOfferTemplate(offer_id, body, options)
  }

  /**
   * 
   * @summary edit_collective_stock <PATCH>
   * @param {number} collective_stock_id 
   * @param {CollectiveStockEditionBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public editCollectiveStock(collective_stock_id: number, body?: CollectiveStockEditionBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).editCollectiveStock(collective_stock_id, body, options)
  }

  /**
   * 
   * @summary edit_venue <PATCH>
   * @param {number} venue_id 
   * @param {EditVenueBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public editVenue(venue_id: number, body?: EditVenueBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).editVenue(venue_id, body, options)
  }

  /**
   * 
   * @summary edit_venue_collective_data <PATCH>
   * @param {number} venue_id 
   * @param {EditVenueCollectiveDataBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public editVenueCollectiveData(venue_id: number, body?: EditVenueCollectiveDataBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).editVenueCollectiveData(venue_id, body, options)
  }

  /**
   * 
   * @summary export_bookings_for_offer_as_csv <GET>
   * @param {number} offer_id 
   * @param {BookingsExportStatusFilter} status 
   * @param {string} event_date 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public exportBookingsForOfferAsCsv(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any) {
    return DefaultApiFp(this.configuration).exportBookingsForOfferAsCsv(offer_id, status, event_date, options)
  }

  /**
   * 
   * @summary export_bookings_for_offer_as_excel <GET>
   * @param {number} offer_id 
   * @param {BookingsExportStatusFilter} status 
   * @param {string} event_date 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public exportBookingsForOfferAsExcel(offer_id: number, status: BookingsExportStatusFilter, event_date: string, options?: any) {
    return DefaultApiFp(this.configuration).exportBookingsForOfferAsExcel(offer_id, status, event_date, options)
  }

  /**
   * 
   * @summary fetch_venue_labels <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public fetchVenueLabels(options?: any) {
    return DefaultApiFp(this.configuration).fetchVenueLabels(options)
  }

  /**
   * 
   * @summary get_autocomplete_educational_redactors_for_uai <GET>
   * @param {string} uai 
   * @param {string} candidate 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getAutocompleteEducationalRedactorsForUai(uai: string, candidate: string, options?: any) {
    return DefaultApiFp(this.configuration).getAutocompleteEducationalRedactorsForUai(uai, candidate, options)
  }

  /**
   * 
   * @summary get_bank_accounts <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getBankAccounts(options?: any) {
    return DefaultApiFp(this.configuration).getBankAccounts(options)
  }

  /**
   * 
   * @summary get_bookings_csv <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {number} [offerId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {number} [offererAddressId] 
   * @param {ExportType} [exportType] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getBookingsCsv(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType, options?: any) {
    return DefaultApiFp(this.configuration).getBookingsCsv(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
  }

  /**
   * 
   * @summary get_bookings_excel <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {number} [offerId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter1} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {number} [offererAddressId] 
   * @param {ExportType1} [exportType] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getBookingsExcel(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter1, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType1, options?: any) {
    return DefaultApiFp(this.configuration).getBookingsExcel(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
  }

  /**
   * 
   * @summary get_bookings_pro <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {number} [offerId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter2} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {number} [offererAddressId] 
   * @param {ExportType2} [exportType] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getBookingsPro(page?: number, venueId?: number, offerId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter2, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, offererAddressId?: number, exportType?: ExportType2, options?: any) {
    return DefaultApiFp(this.configuration).getBookingsPro(page, venueId, offerId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, offererAddressId, exportType, options)
  }

  /**
   * 
   * @summary get_categories <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCategories(options?: any) {
    return DefaultApiFp(this.configuration).getCategories(options)
  }

  /**
   * 
   * @summary get_collective_booking_by_id <GET>
   * @param {number} booking_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveBookingById(booking_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveBookingById(booking_id, options)
  }

  /**
   * 
   * @summary get_collective_bookings_csv <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter3} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveBookingsCsv(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter3, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveBookingsCsv(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
  }

  /**
   * 
   * @summary get_collective_bookings_excel <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter4} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveBookingsExcel(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter4, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveBookingsExcel(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
  }

  /**
   * 
   * @summary get_collective_bookings_pro <GET>
   * @param {number} [page] 
   * @param {number} [venueId] 
   * @param {string} [eventDate] 
   * @param {BookingStatusFilter5} [bookingStatusFilter] 
   * @param {string} [bookingPeriodBeginningDate] 
   * @param {string} [bookingPeriodEndingDate] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveBookingsPro(page?: number, venueId?: number, eventDate?: string, bookingStatusFilter?: BookingStatusFilter5, bookingPeriodBeginningDate?: string, bookingPeriodEndingDate?: string, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveBookingsPro(page, venueId, eventDate, bookingStatusFilter, bookingPeriodBeginningDate, bookingPeriodEndingDate, options)
  }

  /**
   * 
   * @summary get_collective_offer <GET>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOffer(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOffer(offer_id, options)
  }

  /**
   * 
   * @summary get_collective_offer_request <GET>
   * @param {number} request_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOfferRequest(request_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOfferRequest(request_id, options)
  }

  /**
   * 
   * @summary get_collective_offer_template <GET>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOfferTemplate(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOfferTemplate(offer_id, options)
  }

  /**
   * 
   * @summary get_collective_offers <GET>
   * @param {string} [nameOrIsbn] 
   * @param {number} [offererId] 
   * @param {Status} [status] 
   * @param {number} [venueId] 
   * @param {string} [categoryId] 
   * @param {string} [creationMode] 
   * @param {string} [periodBeginningDate] 
   * @param {string} [periodEndingDate] 
   * @param {CollectiveOfferType} [collectiveOfferType] 
   * @param {Format} [format] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOffers(nameOrIsbn?: string, offererId?: number, status?: Status, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType, format?: Format, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, format, options)
  }

  /**
   * 
   * @summary get_combined_invoices <GET>
   * @param {Array<string>} invoiceReferences 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCombinedInvoices(invoiceReferences: Array<string>, options?: any) {
    return DefaultApiFp(this.configuration).getCombinedInvoices(invoiceReferences, options)
  }

  /**
   * 
   * @summary get_educational_institutions <GET>
   * @param {number} [perPageLimit] 
   * @param {number} [page] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getEducationalInstitutions(perPageLimit?: number, page?: number, options?: any) {
    return DefaultApiFp(this.configuration).getEducationalInstitutions(perPageLimit, page, options)
  }

  /**
   * 
   * @summary get_educational_partners <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getEducationalPartners(options?: any) {
    return DefaultApiFp(this.configuration).getEducationalPartners(options)
  }

  /**
   * 
   * @summary get_invoices_v2 <GET>
   * @param {string} [periodBeginningDate] 
   * @param {string} [periodEndingDate] 
   * @param {number} [bankAccountId] 
   * @param {number} [offererId] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getInvoicesV2(periodBeginningDate?: string, periodEndingDate?: string, bankAccountId?: number, offererId?: number, options?: any) {
    return DefaultApiFp(this.configuration).getInvoicesV2(periodBeginningDate, periodEndingDate, bankAccountId, offererId, options)
  }

  /**
   * 
   * @summary get_music_types <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getMusicTypes(options?: any) {
    return DefaultApiFp(this.configuration).getMusicTypes(options)
  }

  /**
   * 
   * @summary get_national_programs <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getNationalPrograms(options?: any) {
    return DefaultApiFp(this.configuration).getNationalPrograms(options)
  }

  /**
   * 
   * @summary get_offer <GET>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffer(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffer(offer_id, options)
  }

  /**
   * 
   * @summary get_offer_price_categories_and_schedules_by_dates <GET>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOfferPriceCategoriesAndSchedulesByDates(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOfferPriceCategoriesAndSchedulesByDates(offer_id, options)
  }

  /**
   * 
   * @summary get_offerer <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOfferer(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOfferer(offerer_id, options)
  }

  /**
   * 
   * @summary get_offerer_addresses <GET>
   * @param {number} offerer_id 
   * @param {boolean} [onlyWithOffers] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererAddresses(offerer_id: number, onlyWithOffers?: boolean, options?: any) {
    return DefaultApiFp(this.configuration).getOffererAddresses(offerer_id, onlyWithOffers, options)
  }

  /**
   * 
   * @summary get_offerer_bank_accounts_and_attached_venues <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererBankAccountsAndAttachedVenues(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffererBankAccountsAndAttachedVenues(offerer_id, options)
  }

  /**
   * 
   * @summary get_offerer_members <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererMembers(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffererMembers(offerer_id, options)
  }

  /**
   * 
   * @summary get_offerer_stats <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererStats(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffererStats(offerer_id, options)
  }

  /**
   * 
   * @summary get_offerer_stats_dashboard_url <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererStatsDashboardUrl(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffererStatsDashboardUrl(offerer_id, options)
  }

  /**
   * 
   * @summary get_offerer_v2_stats <GET>
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getOffererV2Stats(offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getOffererV2Stats(offerer_id, options)
  }

  /**
   * 
   * @summary get_product_by_ean <GET>
   * @param {string} ean 
   * @param {number} offerer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getProductByEan(ean: string, offerer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getProductByEan(ean, offerer_id, options)
  }

  /**
   * 
   * @summary get_profile <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getProfile(options?: any) {
    return DefaultApiFp(this.configuration).getProfile(options)
  }

  /**
   * 
   * @summary get_providers_by_venue <GET>
   * @param {number} venue_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getProvidersByVenue(venue_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getProvidersByVenue(venue_id, options)
  }

  /**
   * 
   * @summary get_reimbursements_csv <GET>
   * @param {number} offererId 
   * @param {number} [bankAccountId] 
   * @param {string} [reimbursementPeriodBeginningDate] 
   * @param {string} [reimbursementPeriodEndingDate] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getReimbursementsCsv(offererId: number, bankAccountId?: number, reimbursementPeriodBeginningDate?: string, reimbursementPeriodEndingDate?: string, options?: any) {
    return DefaultApiFp(this.configuration).getReimbursementsCsv(offererId, bankAccountId, reimbursementPeriodBeginningDate, reimbursementPeriodEndingDate, options)
  }

  /**
   * 
   * @summary get_reimbursements_csv_v2 <GET>
   * @param {Array<string>} invoicesReferences 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getReimbursementsCsvV2(invoicesReferences: Array<string>, options?: any) {
    return DefaultApiFp(this.configuration).getReimbursementsCsvV2(invoicesReferences, options)
  }

  /**
   * 
   * @summary get_siren_info <GET>
   * @param {string} siren 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getSirenInfo(siren: string, options?: any) {
    return DefaultApiFp(this.configuration).getSirenInfo(siren, options)
  }

  /**
   * 
   * @summary get_siret_info <GET>
   * @param {string} siret 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getSiretInfo(siret: string, options?: any) {
    return DefaultApiFp(this.configuration).getSiretInfo(siret, options)
  }

  /**
   * 
   * @summary get_statistics <GET>
   * @param {VenueIds} [venue_ids] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getStatistics(venue_ids?: VenueIds, options?: any) {
    return DefaultApiFp(this.configuration).getStatistics(venue_ids, options)
  }

  /**
   * 
   * @summary get_stocks <GET>
   * @param {number} offer_id 
   * @param {string} [date] 
   * @param {string} [time] 
   * @param {number} [price_category_id] 
   * @param {OrderBy} [order_by] 
   * @param {boolean} [order_by_desc] 
   * @param {number} [page] 
   * @param {number} [stocks_limit_per_page] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getStocks(offer_id: number, date?: string, time?: string, price_category_id?: number, order_by?: OrderBy, order_by_desc?: boolean, page?: number, stocks_limit_per_page?: number, options?: any) {
    return DefaultApiFp(this.configuration).getStocks(offer_id, date, time, price_category_id, order_by, order_by_desc, page, stocks_limit_per_page, options)
  }

  /**
   * 
   * @summary get_stocks_stats <GET>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getStocksStats(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getStocksStats(offer_id, options)
  }

  /**
   * 
   * @summary get_suggested_subcategories <GET>
   * @param {string} offer_name 
   * @param {string} [offer_description] 
   * @param {number} [venue_id] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getSuggestedSubcategories(offer_name: string, offer_description?: string, venue_id?: number, options?: any) {
    return DefaultApiFp(this.configuration).getSuggestedSubcategories(offer_name, offer_description, venue_id, options)
  }

  /**
   * 
   * @summary get_user_email_pending_validation <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getUserEmailPendingValidation(options?: any) {
    return DefaultApiFp(this.configuration).getUserEmailPendingValidation(options)
  }

  /**
   * 
   * @summary get_user_has_bookings <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getUserHasBookings(options?: any) {
    return DefaultApiFp(this.configuration).getUserHasBookings(options)
  }

  /**
   * 
   * @summary get_user_has_collective_bookings <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getUserHasCollectiveBookings(options?: any) {
    return DefaultApiFp(this.configuration).getUserHasCollectiveBookings(options)
  }

  /**
   * 
   * @summary get_venue <GET>
   * @param {number} venue_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenue(venue_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getVenue(venue_id, options)
  }

  /**
   * 
   * @summary get_venue_stats_dashboard_url <GET>
   * @param {number} venue_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenueStatsDashboardUrl(venue_id: number, options?: any) {
    return DefaultApiFp(this.configuration).getVenueStatsDashboardUrl(venue_id, options)
  }

  /**
   * 
   * @summary get_venue_types <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenueTypes(options?: any) {
    return DefaultApiFp(this.configuration).getVenueTypes(options)
  }

  /**
   * 
   * @summary get_venues <GET>
   * @param {boolean} [validated] 
   * @param {boolean} [activeOfferersOnly] 
   * @param {number} [offererId] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenues(validated?: boolean, activeOfferersOnly?: boolean, offererId?: number, options?: any) {
    return DefaultApiFp(this.configuration).getVenues(validated, activeOfferersOnly, offererId, options)
  }

  /**
   * 
   * @summary get_venues_educational_statuses <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenuesEducationalStatuses(options?: any) {
    return DefaultApiFp(this.configuration).getVenuesEducationalStatuses(options)
  }

  /**
   * 
   * @summary get_venues_of_offerer_from_siret <GET>
   * @param {string} siret 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenuesOfOffererFromSiret(siret: string, options?: any) {
    return DefaultApiFp(this.configuration).getVenuesOfOffererFromSiret(siret, options)
  }

  /**
   * 
   * @summary has_invoice <GET>
   * @param {number} offererId 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public hasInvoice(offererId: number, options?: any) {
    return DefaultApiFp(this.configuration).hasInvoice(offererId, options)
  }

  /**
   * 
   * @summary invite_member <POST>
   * @param {number} offerer_id 
   * @param {InviteMemberQueryModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public inviteMember(offerer_id: number, body?: InviteMemberQueryModel, options?: any) {
    return DefaultApiFp(this.configuration).inviteMember(offerer_id, body, options)
  }

  /**
   * 
   * @summary link_venue_to_bank_account <PATCH>
   * @param {number} offerer_id 
   * @param {number} bank_account_id 
   * @param {LinkVenueToBankAccountBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public linkVenueToBankAccount(offerer_id: number, bank_account_id: number, body?: LinkVenueToBankAccountBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).linkVenueToBankAccount(offerer_id, bank_account_id, body, options)
  }

  /**
   * 
   * @summary link_venue_to_pricing_point <POST>
   * @param {number} venue_id 
   * @param {LinkVenueToPricingPointBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public linkVenueToPricingPoint(venue_id: number, body?: LinkVenueToPricingPointBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).linkVenueToPricingPoint(venue_id, body, options)
  }

  /**
   * 
   * @summary list_educational_domains <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listEducationalDomains(options?: any) {
    return DefaultApiFp(this.configuration).listEducationalDomains(options)
  }

  /**
   * 
   * @summary list_educational_offerers <GET>
   * @param {number} [offerer_id] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listEducationalOfferers(offerer_id?: number, options?: any) {
    return DefaultApiFp(this.configuration).listEducationalOfferers(offerer_id, options)
  }

  /**
   * 
   * @summary list_features <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listFeatures(options?: any) {
    return DefaultApiFp(this.configuration).listFeatures(options)
  }

  /**
   * 
   * @summary list_offerers_names <GET>
   * @param {boolean} [validated] 
   * @param {boolean} [validated_for_user] 
   * @param {number} [offerer_id] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listOfferersNames(validated?: boolean, validated_for_user?: boolean, offerer_id?: number, options?: any) {
    return DefaultApiFp(this.configuration).listOfferersNames(validated, validated_for_user, offerer_id, options)
  }

  /**
   * 
   * @summary list_offers <GET>
   * @param {string} [nameOrIsbn] 
   * @param {number} [offererId] 
   * @param {Status1} [status] 
   * @param {number} [venueId] 
   * @param {string} [categoryId] 
   * @param {string} [creationMode] 
   * @param {string} [periodBeginningDate] 
   * @param {string} [periodEndingDate] 
   * @param {CollectiveOfferType1} [collectiveOfferType] 
   * @param {number} [offererAddressId] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listOffers(nameOrIsbn?: string, offererId?: number, status?: Status1, venueId?: number, categoryId?: string, creationMode?: string, periodBeginningDate?: string, periodEndingDate?: string, collectiveOfferType?: CollectiveOfferType1, offererAddressId?: number, options?: any) {
    return DefaultApiFp(this.configuration).listOffers(nameOrIsbn, offererId, status, venueId, categoryId, creationMode, periodBeginningDate, periodEndingDate, collectiveOfferType, offererAddressId, options)
  }

  /**
   * 
   * @summary list_venue_providers <GET>
   * @param {number} venueId 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public listVenueProviders(venueId: number, options?: any) {
    return DefaultApiFp(this.configuration).listVenueProviders(venueId, options)
  }

  /**
   * 
   * @summary patch_all_offers_active_status <PATCH>
   * @param {PatchAllOffersActiveStatusBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchAllOffersActiveStatus(body?: PatchAllOffersActiveStatusBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchAllOffersActiveStatus(body, options)
  }

  /**
   * 
   * @summary patch_collective_offer_publication <PATCH>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOfferPublication(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOfferPublication(offer_id, options)
  }

  /**
   * 
   * @summary patch_collective_offer_template_publication <PATCH>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOfferTemplatePublication(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOfferTemplatePublication(offer_id, options)
  }

  /**
   * 
   * @summary patch_collective_offers_active_status <PATCH>
   * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOffersActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOffersActiveStatus(body, options)
  }

  /**
   * 
   * @summary patch_collective_offers_archive <PATCH>
   * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOffersArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOffersArchive(body, options)
  }

  /**
   * 
   * @summary patch_collective_offers_educational_institution <PATCH>
   * @param {number} offer_id 
   * @param {PatchCollectiveOfferEducationalInstitution} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOffersEducationalInstitution(offer_id: number, body?: PatchCollectiveOfferEducationalInstitution, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOffersEducationalInstitution(offer_id, body, options)
  }

  /**
   * 
   * @summary patch_collective_offers_template_active_status <PATCH>
   * @param {PatchCollectiveOfferActiveStatusBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOffersTemplateActiveStatus(body?: PatchCollectiveOfferActiveStatusBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOffersTemplateActiveStatus(body, options)
  }

  /**
   * 
   * @summary patch_collective_offers_template_archive <PATCH>
   * @param {PatchCollectiveOfferArchiveBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchCollectiveOffersTemplateArchive(body?: PatchCollectiveOfferArchiveBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchCollectiveOffersTemplateArchive(body, options)
  }

  /**
   * 
   * @summary patch_draft_offer <PATCH>
   * @param {number} offer_id 
   * @param {PatchDraftOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchDraftOffer(offer_id: number, body?: PatchDraftOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchDraftOffer(offer_id, body, options)
  }

  /**
   * 
   * @summary patch_offer <PATCH>
   * @param {number} offer_id 
   * @param {PatchOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchOffer(offer_id: number, body?: PatchOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchOffer(offer_id, body, options)
  }

  /**
   * 
   * @summary patch_offers_active_status <PATCH>
   * @param {PatchOfferActiveStatusBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchOffersActiveStatus(body?: PatchOfferActiveStatusBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchOffersActiveStatus(body, options)
  }

  /**
   * 
   * @summary patch_pro_user_rgs_seen <PATCH>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchProUserRgsSeen(options?: any) {
    return DefaultApiFp(this.configuration).patchProUserRgsSeen(options)
  }

  /**
   * 
   * @summary patch_publish_offer <PATCH>
   * @param {PatchOfferPublishBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchPublishOffer(body?: PatchOfferPublishBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchPublishOffer(body, options)
  }

  /**
   * 
   * @summary patch_user_identity <PATCH>
   * @param {UserIdentityBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchUserIdentity(body?: UserIdentityBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchUserIdentity(body, options)
  }

  /**
   * 
   * @summary patch_user_phone <PATCH>
   * @param {UserPhoneBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchUserPhone(body?: UserPhoneBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).patchUserPhone(body, options)
  }

  /**
   * 
   * @summary patch_user_tuto_seen <PATCH>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchUserTutoSeen(options?: any) {
    return DefaultApiFp(this.configuration).patchUserTutoSeen(options)
  }

  /**
   * 
   * @summary patch_validate_email <PATCH>
   * @param {ChangeProEmailBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public patchValidateEmail(body?: ChangeProEmailBody, options?: any) {
    return DefaultApiFp(this.configuration).patchValidateEmail(body, options)
  }

  /**
   * 
   * @summary post_change_password <POST>
   * @param {ChangePasswordBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postChangePassword(body?: ChangePasswordBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postChangePassword(body, options)
  }

  /**
   * 
   * @summary post_create_venue <POST>
   * @param {PostVenueBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postCreateVenue(body?: PostVenueBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postCreateVenue(body, options)
  }

  /**
   * 
   * @summary post_draft_offer <POST>
   * @param {PostDraftOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postDraftOffer(body?: PostDraftOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postDraftOffer(body, options)
  }

  /**
   * 
   * @summary post_new_password <POST>
   * @param {NewPasswordBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postNewPassword(body?: NewPasswordBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postNewPassword(body, options)
  }

  /**
   * 
   * @summary post_offer <POST>
   * @param {PostOfferBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postOffer(body?: PostOfferBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postOffer(body, options)
  }

  /**
   * 
   * @summary post_price_categories <POST>
   * @param {number} offer_id 
   * @param {PriceCategoryBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postPriceCategories(offer_id: number, body?: PriceCategoryBody, options?: any) {
    return DefaultApiFp(this.configuration).postPriceCategories(offer_id, body, options)
  }

  /**
   * 
   * @summary post_pro_flags <POST>
   * @param {ProFlagsQueryModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postProFlags(body?: ProFlagsQueryModel, options?: any) {
    return DefaultApiFp(this.configuration).postProFlags(body, options)
  }

  /**
   * 
   * @summary post_user_email <POST>
   * @param {UserResetEmailBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postUserEmail(body?: UserResetEmailBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).postUserEmail(body, options)
  }

  /**
   * 
   * @summary reset_password <POST>
   * @param {ResetPasswordBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public resetPassword(body?: ResetPasswordBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).resetPassword(body, options)
  }

  /**
   * 
   * @summary save_new_onboarding_data <POST>
   * @param {SaveNewOnboardingDataQueryModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public saveNewOnboardingData(body?: SaveNewOnboardingDataQueryModel, options?: any) {
    return DefaultApiFp(this.configuration).saveNewOnboardingData(body, options)
  }

  /**
   * 
   * @summary signin <POST>
   * @param {LoginUserBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public signin(body?: LoginUserBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).signin(body, options)
  }

  /**
   * 
   * @summary signout <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public signout(options?: any) {
    return DefaultApiFp(this.configuration).signout(options)
  }

  /**
   * 
   * @summary signup_pro_V2 <POST>
   * @param {ProUserCreationBodyV2Model} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public signupProV2(body?: ProUserCreationBodyV2Model, options?: any) {
    return DefaultApiFp(this.configuration).signupProV2(body, options)
  }

  /**
   * 
   * @summary submit_user_review <POST>
   * @param {SubmitReviewRequestModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public submitUserReview(body?: SubmitReviewRequestModel, options?: any) {
    return DefaultApiFp(this.configuration).submitUserReview(body, options)
  }

  /**
   * 
   * @summary update_venue_provider <PUT>
   * @param {PostVenueProviderBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public updateVenueProvider(body?: PostVenueProviderBody, options?: any) {
    return DefaultApiFp(this.configuration).updateVenueProvider(body, options)
  }

  /**
   * 
   * @summary upsert_stocks <POST>
   * @param {StocksUpsertBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public upsertStocks(body?: StocksUpsertBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).upsertStocks(body, options)
  }

  /**
   * 
   * @summary validate_user <PATCH>
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public validateUser(token: string, options?: any) {
    return DefaultApiFp(this.configuration).validateUser(token, options)
  }

}
