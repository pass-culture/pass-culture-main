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
 */
export type AcademiesResponseModel = Array<string>
/**
 * 
 * @export
 * @interface AdageBaseModel
 */
export interface AdageBaseModel {
  /**
   * 
   * @type {string}
   * @memberof AdageBaseModel
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof AdageBaseModel
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof AdageBaseModel
   */
  queryId?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum AdageFrontRoles {
  Redactor = <any> 'redactor',
  Readonly = <any> 'readonly'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum AdageHeaderLink {
  Search = <any> 'search',
  MyInstitutionOffers = <any> 'my_institution_offers',
  AdageLink = <any> 'adage_link',
  MyFavorites = <any> 'my_favorites',
  Discovery = <any> 'discovery'
}
/**
 * 
 * @export
 * @interface AdageHeaderLogBody
 */
export interface AdageHeaderLogBody {
  /**
   * 
   * @type {AdageHeaderLink}
   * @memberof AdageHeaderLogBody
   */
  header_link_name: AdageHeaderLink
  /**
   * 
   * @type {string}
   * @memberof AdageHeaderLogBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof AdageHeaderLogBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof AdageHeaderLogBody
   */
  queryId?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum AdagePlaylistType {
  Offer = <any> 'offer',
  Venue = <any> 'venue',
  Domain = <any> 'domain'
}
/**
 * 
 * @export
 * @interface AuthenticatedResponse
 */
export interface AuthenticatedResponse {
  /**
   * 
   * @type {string}
   * @memberof AuthenticatedResponse
   */
  departmentCode?: string
  /**
   * 
   * @type {string}
   * @memberof AuthenticatedResponse
   */
  email?: string
  /**
   * 
   * @type {number}
   * @memberof AuthenticatedResponse
   */
  favoritesCount?: number
  /**
   * 
   * @type {string}
   * @memberof AuthenticatedResponse
   */
  institutionCity?: string
  /**
   * 
   * @type {string}
   * @memberof AuthenticatedResponse
   */
  institutionName?: string
  /**
   * 
   * @type {InstitutionRuralLevel}
   * @memberof AuthenticatedResponse
   */
  institutionRuralLevel?: InstitutionRuralLevel
  /**
   * 
   * @type {number}
   * @memberof AuthenticatedResponse
   */
  lat?: number
  /**
   * 
   * @type {number}
   * @memberof AuthenticatedResponse
   */
  lon?: number
  /**
   * 
   * @type {number}
   * @memberof AuthenticatedResponse
   */
  offersCount?: number
  /**
   * 
   * @type {RedactorPreferences}
   * @memberof AuthenticatedResponse
   */
  preferences?: RedactorPreferences
  /**
   * 
   * @type {Array<EducationalInstitutionProgramModel>}
   * @memberof AuthenticatedResponse
   */
  programs?: Array<EducationalInstitutionProgramModel>
  /**
   * 
   * @type {AdageFrontRoles}
   * @memberof AuthenticatedResponse
   */
  role: AdageFrontRoles
  /**
   * 
   * @type {string}
   * @memberof AuthenticatedResponse
   */
  uai?: string
}
/**
 * 
 * @export
 * @interface BookCollectiveOfferRequest
 */
export interface BookCollectiveOfferRequest {
  /**
   * 
   * @type {number}
   * @memberof BookCollectiveOfferRequest
   */
  stockId: number
}
/**
 * 
 * @export
 * @interface BookCollectiveOfferResponse
 */
export interface BookCollectiveOfferResponse {
  /**
   * 
   * @type {number}
   * @memberof BookCollectiveOfferResponse
   */
  bookingId: number
}
/**
 * 
 * @export
 * @interface CatalogViewBody
 */
export interface CatalogViewBody {
  /**
   * 
   * @type {string}
   * @memberof CatalogViewBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof CatalogViewBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof CatalogViewBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof CatalogViewBody
   */
  source: string
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
   * @type {string}
   * @memberof CategoryResponseModel
   */
  proLabel: string
}
/**
 * 
 * @export
 * @interface CollectiveOfferOfferVenue
 */
export interface CollectiveOfferOfferVenue {
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  address?: string
  /**
   * 
   * @type {OfferAddressType}
   * @memberof CollectiveOfferOfferVenue
   */
  addressType: OfferAddressType
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  city?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferOfferVenue
   */
  distance?: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  name?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  otherAddress: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferOfferVenue
   */
  publicName?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferOfferVenue
   */
  venueId?: number
}
/**
 * 
 * @export
 * @interface CollectiveOfferResponseModel
 */
export interface CollectiveOfferResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  contactEmail?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  description?: string
  /**
   * 
   * @type {Array<OfferDomain>}
   * @memberof CollectiveOfferResponseModel
   */
  domains: Array<OfferDomain>
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {EducationalInstitutionResponseModel}
   * @memberof CollectiveOfferResponseModel
   */
  educationalInstitution?: EducationalInstitutionResponseModel
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferResponseModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof CollectiveOfferResponseModel
   */
  formats?: Array<EacFormat>
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
  isExpired: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isFavorite?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isSoldOut: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  isTemplate?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  motorDisabilityCompliant?: boolean
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
   * @type {number}
   * @memberof CollectiveOfferResponseModel
   */
  offerId?: number
  /**
   * 
   * @type {CollectiveOfferOfferVenue}
   * @memberof CollectiveOfferResponseModel
   */
  offerVenue: CollectiveOfferOfferVenue
  /**
   * 
   * @type {OfferStockResponse}
   * @memberof CollectiveOfferResponseModel
   */
  stock: OfferStockResponse
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof CollectiveOfferResponseModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {EducationalRedactorResponseModel}
   * @memberof CollectiveOfferResponseModel
   */
  teacher?: EducationalRedactorResponseModel
  /**
   * 
   * @type {OfferVenueResponse}
   * @memberof CollectiveOfferResponseModel
   */
  venue: OfferVenueResponse
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface CollectiveOfferTemplateResponseModel
 */
export interface CollectiveOfferTemplateResponseModel {
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  audioDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  contactEmail?: string
  /**
   * 
   * @type {OfferContactFormEnum}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  contactForm?: OfferContactFormEnum
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  contactPhone?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  contactUrl?: string
  /**
   * 
   * @type {TemplateDatesModel}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  dates?: TemplateDatesModel
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  description?: string
  /**
   * 
   * @type {Array<OfferDomain>}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  domains: Array<OfferDomain>
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  durationMinutes?: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  formats?: Array<EacFormat>
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  imageCredit?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  imageUrl?: string
  /**
   * 
   * @type {Array<string>}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  interventionArea: Array<string>
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  isExpired: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  isFavorite?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  isSoldOut: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  isTemplate?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  mentalDisabilityCompliant?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  motorDisabilityCompliant?: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  name: string
  /**
   * 
   * @type {NationalProgramModel}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  nationalProgram?: NationalProgramModel
  /**
   * 
   * @type {number}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  offerId?: number
  /**
   * 
   * @type {CollectiveOfferOfferVenue}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  offerVenue: CollectiveOfferOfferVenue
  /**
   * 
   * @type {Array<StudentLevels>}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  students: Array<StudentLevels>
  /**
   * 
   * @type {OfferVenueResponse}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  venue: OfferVenueResponse
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveOfferTemplateResponseModel
   */
  visualDisabilityCompliant?: boolean
}
/**
 * 
 * @export
 * @interface CollectiveRequestBody
 */
export interface CollectiveRequestBody {
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestBody
   */
  collectiveOfferTemplateId: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestBody
   */
  comment: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof CollectiveRequestBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestBody
   */
  phoneNumber?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestBody
   */
  requestedDate?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestBody
   */
  totalStudents?: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestBody
   */
  totalTeachers?: number
}
/**
 * 
 * @export
 * @interface CollectiveRequestResponseModel
 */
export interface CollectiveRequestResponseModel {
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestResponseModel
   */
  comment: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestResponseModel
   */
  email: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestResponseModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {string}
   * @memberof CollectiveRequestResponseModel
   */
  requestedDate?: string
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestResponseModel
   */
  totalStudents?: number
  /**
   * 
   * @type {number}
   * @memberof CollectiveRequestResponseModel
   */
  totalTeachers?: number
}
/**
 * 
 * @export
 * @interface Coordinates
 */
export interface Coordinates {
  /**
   * 
   * @type {number}
   * @memberof Coordinates
   */
  latitude?: number
  /**
   * 
   * @type {number}
   * @memberof Coordinates
   */
  longitude?: number
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
 * @interface EacFormatsResponseModel
 */
export interface EacFormatsResponseModel {
  /**
   * 
   * @type {Array<EacFormat>}
   * @memberof EacFormatsResponseModel
   */
  formats: Array<EacFormat>
}
/**
 * 
 * @export
 * @interface EducationalInstitutionProgramModel
 */
export interface EducationalInstitutionProgramModel {
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionProgramModel
   */
  description?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionProgramModel
   */
  label?: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionProgramModel
   */
  name: string
}
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
  postalCode: string
}
/**
 * 
 * @export
 * @interface EducationalInstitutionWithBudgetResponseModel
 */
export interface EducationalInstitutionWithBudgetResponseModel {
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  budget: number
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  city: string
  /**
   * 
   * @type {number}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  institutionType: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  phoneNumber: string
  /**
   * 
   * @type {string}
   * @memberof EducationalInstitutionWithBudgetResponseModel
   */
  postalCode: string
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
 * @interface FavoritesResponseModel
 */
export interface FavoritesResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferResponseModel>}
   * @memberof FavoritesResponseModel
   */
  favoritesOffer: Array<CollectiveOfferResponseModel>
  /**
   * 
   * @type {Array<CollectiveOfferTemplateResponseModel>}
   * @memberof FavoritesResponseModel
   */
  favoritesTemplate: Array<CollectiveOfferTemplateResponseModel>
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
 * @interface GetRelativeVenuesQueryModel
 */
export interface GetRelativeVenuesQueryModel {
  /**
   * 
   * @type {boolean}
   * @memberof GetRelativeVenuesQueryModel
   */
  getRelative?: boolean
}
/**
 * 
 * @export
 * @interface GetTemplateIdsModel
 */
export interface GetTemplateIdsModel {
  /**
   * 
   * @type {Array<number>}
   * @memberof GetTemplateIdsModel
   */
  ids: Array<number>
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum InstitutionRuralLevel {
  GrandsCentresUrbains = <any> 'Grands centres urbains',
  CeinturesUrbaines = <any> 'Ceintures urbaines',
  CentresUrbainsIntermdiaires = <any> 'Centres urbains intermédiaires',
  PetitesVilles = <any> 'Petites villes',
  BourgsRuraux = <any> 'Bourgs ruraux',
  RuralHabitatDispers = <any> 'Rural à habitat dispersé',
  RuralHabitatTrsDispers = <any> 'Rural à habitat très dispersé'
}
/**
 * 
 * @export
 * @interface ListCollectiveOfferTemplateResponseModel
 */
export interface ListCollectiveOfferTemplateResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferTemplateResponseModel>}
   * @memberof ListCollectiveOfferTemplateResponseModel
   */
  collectiveOffers: Array<CollectiveOfferTemplateResponseModel>
}
/**
 * 
 * @export
 * @interface ListCollectiveOffersResponseModel
 */
export interface ListCollectiveOffersResponseModel {
  /**
   * 
   * @type {Array<CollectiveOfferResponseModel>}
   * @memberof ListCollectiveOffersResponseModel
   */
  collectiveOffers: Array<CollectiveOfferResponseModel>
}
/**
 * 
 * @export
 */
export type ListFeatureResponseModel = Array<FeatureResponseModel>
/**
 * 
 * @export
 * @interface LocalOfferersPlaylist
 */
export interface LocalOfferersPlaylist {
  /**
   * 
   * @type {Array<LocalOfferersPlaylistOffer>}
   * @memberof LocalOfferersPlaylist
   */
  venues: Array<LocalOfferersPlaylistOffer>
}
/**
 * 
 * @export
 * @interface LocalOfferersPlaylistOffer
 */
export interface LocalOfferersPlaylistOffer {
  /**
   * 
   * @type {string}
   * @memberof LocalOfferersPlaylistOffer
   */
  city?: string
  /**
   * 
   * @type {number}
   * @memberof LocalOfferersPlaylistOffer
   */
  distance?: number
  /**
   * 
   * @type {number}
   * @memberof LocalOfferersPlaylistOffer
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof LocalOfferersPlaylistOffer
   */
  imgUrl?: string
  /**
   * 
   * @type {string}
   * @memberof LocalOfferersPlaylistOffer
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof LocalOfferersPlaylistOffer
   */
  publicName?: string
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
 * @interface OfferFavoriteBody
 */
export interface OfferFavoriteBody {
  /**
   * 
   * @type {string}
   * @memberof OfferFavoriteBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof OfferFavoriteBody
   */
  isFavorite: boolean
  /**
   * 
   * @type {boolean}
   * @memberof OfferFavoriteBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {number}
   * @memberof OfferFavoriteBody
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof OfferFavoriteBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof OfferFavoriteBody
   */
  vueType?: string
}
/**
 * 
 * @export
 * @interface OfferIdBody
 */
export interface OfferIdBody {
  /**
   * 
   * @type {string}
   * @memberof OfferIdBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof OfferIdBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {number}
   * @memberof OfferIdBody
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof OfferIdBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof OfferIdBody
   */
  vueType?: string
}
/**
 * 
 * @export
 * @interface OfferListSwitch
 */
export interface OfferListSwitch {
  /**
   * 
   * @type {string}
   * @memberof OfferListSwitch
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof OfferListSwitch
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof OfferListSwitch
   */
  isMobile?: boolean
  /**
   * 
   * @type {string}
   * @memberof OfferListSwitch
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof OfferListSwitch
   */
  source: string
}
/**
 * 
 * @export
 * @interface OfferManagingOffererResponse
 */
export interface OfferManagingOffererResponse {
  /**
   * 
   * @type {string}
   * @memberof OfferManagingOffererResponse
   */
  name: string
}
/**
 * 
 * @export
 * @interface OfferStockResponse
 */
export interface OfferStockResponse {
  /**
   * 
   * @type {string}
   * @memberof OfferStockResponse
   */
  beginningDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof OfferStockResponse
   */
  bookingLimitDatetime?: string
  /**
   * 
   * @type {string}
   * @memberof OfferStockResponse
   */
  educationalPriceDetail?: string
  /**
   * 
   * @type {string}
   * @memberof OfferStockResponse
   */
  endDatetime?: string
  /**
   * 
   * @type {number}
   * @memberof OfferStockResponse
   */
  id: number
  /**
   * 
   * @type {boolean}
   * @memberof OfferStockResponse
   */
  isBookable: boolean
  /**
   * 
   * @type {number}
   * @memberof OfferStockResponse
   */
  numberOfTickets?: number
  /**
   * 
   * @type {number}
   * @memberof OfferStockResponse
   */
  price: number
  /**
   * 
   * @type {string}
   * @memberof OfferStockResponse
   */
  startDatetime?: string
}
/**
 * 
 * @export
 * @interface OfferVenueResponse
 */
export interface OfferVenueResponse {
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  adageId?: string
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  address?: string
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  city?: string
  /**
   * 
   * @type {Coordinates}
   * @memberof OfferVenueResponse
   */
  coordinates: Coordinates
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  departmentCode?: string
  /**
   * 
   * @type {number}
   * @memberof OfferVenueResponse
   */
  distance?: number
  /**
   * 
   * @type {number}
   * @memberof OfferVenueResponse
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  imgUrl?: string
  /**
   * 
   * @type {OfferManagingOffererResponse}
   * @memberof OfferVenueResponse
   */
  managingOfferer: OfferManagingOffererResponse
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  postalCode?: string
  /**
   * 
   * @type {string}
   * @memberof OfferVenueResponse
   */
  publicName?: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum PaginationType {
  Next = <any> 'next',
  Previous = <any> 'previous'
}
/**
 * 
 * @export
 * @interface PlaylistBody
 */
export interface PlaylistBody {
  /**
   * 
   * @type {number}
   * @memberof PlaylistBody
   */
  elementId?: number
  /**
   * 
   * @type {string}
   * @memberof PlaylistBody
   */
  iframeFrom: string
  /**
   * 
   * @type {number}
   * @memberof PlaylistBody
   */
  index?: number
  /**
   * 
   * @type {boolean}
   * @memberof PlaylistBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {number}
   * @memberof PlaylistBody
   */
  playlistId: number
  /**
   * 
   * @type {AdagePlaylistType}
   * @memberof PlaylistBody
   */
  playlistType: AdagePlaylistType
  /**
   * 
   * @type {string}
   * @memberof PlaylistBody
   */
  queryId?: string
}
/**
 * 
 * @export
 * @interface PostCollectiveRequestBodyModel
 */
export interface PostCollectiveRequestBodyModel {
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveRequestBodyModel
   */
  comment: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveRequestBodyModel
   */
  phoneNumber?: string
  /**
   * 
   * @type {string}
   * @memberof PostCollectiveRequestBodyModel
   */
  requestedDate?: string
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveRequestBodyModel
   */
  totalStudents?: number
  /**
   * 
   * @type {number}
   * @memberof PostCollectiveRequestBodyModel
   */
  totalTeachers?: number
}
/**
 * 
 * @export
 * @interface RedactorPreferences
 */
export interface RedactorPreferences {
  /**
   * 
   * @type {boolean}
   * @memberof RedactorPreferences
   */
  broadcast_help_closed?: boolean
  /**
   * 
   * @type {boolean}
   * @memberof RedactorPreferences
   */
  feedback_form_closed?: boolean
}
/**
 * 
 * @export
 * @interface SearchBody
 */
export interface SearchBody {
  /**
   * 
   * @type {Array<string>}
   * @memberof SearchBody
   */
  filters: Array<string>
  /**
   * 
   * @type {string}
   * @memberof SearchBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof SearchBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof SearchBody
   */
  queryId?: string
  /**
   * 
   * @type {number}
   * @memberof SearchBody
   */
  resultsCount: number
}
/**
 * 
 * @export
 * @interface StockIdBody
 */
export interface StockIdBody {
  /**
   * 
   * @type {string}
   * @memberof StockIdBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof StockIdBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof StockIdBody
   */
  queryId?: string
  /**
   * 
   * @type {number}
   * @memberof StockIdBody
   */
  stockId: number
  /**
   * 
   * @type {string}
   * @memberof StockIdBody
   */
  vueType?: string
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
  categoryId: string
  /**
   * 
   * @type {string}
   * @memberof SubcategoryResponseModel
   */
  id: string
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum SuggestionType {
  Venue = <any> 'venue',
  OfferCategory = <any> 'offer category',
  Offer = <any> 'offer'
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
 * @interface TrackingAutocompleteSuggestionBody
 */
export interface TrackingAutocompleteSuggestionBody {
  /**
   * 
   * @type {string}
   * @memberof TrackingAutocompleteSuggestionBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof TrackingAutocompleteSuggestionBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof TrackingAutocompleteSuggestionBody
   */
  queryId?: string
  /**
   * 
   * @type {SuggestionType}
   * @memberof TrackingAutocompleteSuggestionBody
   */
  suggestionType: SuggestionType
  /**
   * 
   * @type {string}
   * @memberof TrackingAutocompleteSuggestionBody
   */
  suggestionValue: string
}
/**
 * 
 * @export
 * @interface TrackingCTAShareBody
 */
export interface TrackingCTAShareBody {
  /**
   * 
   * @type {string}
   * @memberof TrackingCTAShareBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof TrackingCTAShareBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {number}
   * @memberof TrackingCTAShareBody
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof TrackingCTAShareBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof TrackingCTAShareBody
   */
  source: string
  /**
   * 
   * @type {string}
   * @memberof TrackingCTAShareBody
   */
  vueType?: string
}
/**
 * 
 * @export
 * @interface TrackingFilterBody
 */
export interface TrackingFilterBody {
  /**
   * 
   * @type {any}
   * @memberof TrackingFilterBody
   */
  filterValues: any
  /**
   * 
   * @type {string}
   * @memberof TrackingFilterBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof TrackingFilterBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof TrackingFilterBody
   */
  queryId?: string
  /**
   * 
   * @type {number}
   * @memberof TrackingFilterBody
   */
  resultNumber: number
}
/**
 * 
 * @export
 * @interface TrackingShowMoreBody
 */
export interface TrackingShowMoreBody {
  /**
   * 
   * @type {string}
   * @memberof TrackingShowMoreBody
   */
  iframeFrom: string
  /**
   * 
   * @type {boolean}
   * @memberof TrackingShowMoreBody
   */
  isFromNoResult?: boolean
  /**
   * 
   * @type {string}
   * @memberof TrackingShowMoreBody
   */
  queryId?: string
  /**
   * 
   * @type {string}
   * @memberof TrackingShowMoreBody
   */
  source: string
  /**
   * 
   * @type {PaginationType}
   * @memberof TrackingShowMoreBody
   */
  type: PaginationType
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
 * @interface VenueResponse
 */
export interface VenueResponse {
  /**
   * 
   * @type {string}
   * @memberof VenueResponse
   */
  adageId?: string
  /**
   * 
   * @type {string}
   * @memberof VenueResponse
   */
  departementCode: string
  /**
   * 
   * @type {number}
   * @memberof VenueResponse
   */
  id: number
  /**
   * 
   * @type {string}
   * @memberof VenueResponse
   */
  name: string
  /**
   * 
   * @type {string}
   * @memberof VenueResponse
   */
  publicName?: string
  /**
   * 
   * @type {Array<number>}
   * @memberof VenueResponse
   */
  relative: Array<number>
}
/**
 * DefaultApi - fetch parameter creator
 * @export
 */
export const DefaultApiFetchParamCreator = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary authenticate <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    authenticate(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/authenticate`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary book_collective_offer <POST>
     * @param {BookCollectiveOfferRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    bookCollectiveOffer(body?: BookCollectiveOfferRequest, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/collective/bookings`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_adage_jwt_fake_token <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createAdageJwtFakeToken(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/testing/token`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary create_collective_request <POST>
     * @param {number} offer_id 
     * @param {PostCollectiveRequestBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveRequest(offer_id: number, body?: PostCollectiveRequestBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling createCollectiveRequest.')
      }
      const localVarPath = `/adage-iframe/collective/offers-template/{offer_id}/request`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOffer(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling deleteFavoriteForCollectiveOffer.')
      }
      const localVarPath = `/adage-iframe/collective/offer/{offer_id}/favorites`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer_template <DELETE>
     * @param {number} offer_template_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOfferTemplate(offer_template_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_template_id' is not null or undefined
      if (offer_template_id === null || offer_template_id === undefined) {
        throw new RequiredError('offer_template_id','Required parameter offer_template_id was null or undefined when calling deleteFavoriteForCollectiveOfferTemplate.')
      }
      const localVarPath = `/adage-iframe/collective/template/{offer_template_id}/favorites`
        .replace(`{${'offer_template_id'}}`, encodeURIComponent(String(offer_template_id)))
      const localVarRequestOptions = Object.assign({ method: 'DELETE', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_academies <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAcademies(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/collective/academies`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_classroom_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getClassroomPlaylist(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/playlists/classroom`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_favorites <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveFavorites(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/collective/favorites`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

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
      const localVarPath = `/adage-iframe/collective/offers/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

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
      const localVarPath = `/adage-iframe/collective/offers-template/{offer_id}`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offer_templates <GET>
     * @param {Array<number>} ids 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplates(ids: Array<number>, options: any = {}): ApiRequestOptions {
      // verify required parameter 'ids' is not null or undefined
      if (ids === null || ids === undefined) {
        throw new RequiredError('ids','Required parameter ids was null or undefined when calling getCollectiveOfferTemplates.')
      }
      const localVarPath = `/adage-iframe/collective/offers-template/`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication JWTAuth required

      if (ids) {
        localVarQueryParameter['ids'] = ids
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_collective_offers_for_my_institution <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffersForMyInstitution(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/collective/offers/my_institution`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_educational_institution_with_budget <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutionWithBudget(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/collective/institution`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_educational_offers_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersCategories(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/offers/categories`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_educational_offers_formats <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersFormats(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/offers/formats`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_local_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getLocalOfferersPlaylist(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/playlists/local-offerers`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_new_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNewOfferersPlaylist(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/playlists/new_offerers`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venue_by_id <GET>
     * @param {number} venue_id 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueById(venue_id: number, getRelative?: boolean, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling getVenueById.')
      }
      const localVarPath = `/adage-iframe/venues/{venue_id}`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication JWTAuth required

      if (getRelative !== undefined) {
        localVarQueryParameter['getRelative'] = getRelative
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary get_venue_by_siret <GET>
     * @param {string} siret 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueBySiret(siret: string, getRelative?: boolean, options: any = {}): ApiRequestOptions {
      // verify required parameter 'siret' is not null or undefined
      if (siret === null || siret === undefined) {
        throw new RequiredError('siret','Required parameter siret was null or undefined when calling getVenueBySiret.')
      }
      const localVarPath = `/adage-iframe/venues/siret/{siret}`
        .replace(`{${'siret'}}`, encodeURIComponent(String(siret)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication JWTAuth required

      if (getRelative !== undefined) {
        localVarQueryParameter['getRelative'] = getRelative
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
      const localVarPath = `/adage-iframe/features`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_booking_modal_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logBookingModalButtonClick(body?: StockIdBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/booking-modal-button`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_catalog_view <POST>
     * @param {CatalogViewBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logCatalogView(body?: CatalogViewBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/catalog-view`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_consult_playlist_element <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logConsultPlaylistElement(body?: PlaylistBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/consult-playlist-element`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_contact_modal_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactModalButtonClick(body?: OfferIdBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/contact-modal-button`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_contact_url_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactUrlClick(body?: OfferIdBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/contact-url-click`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_fav_offer_button_click <POST>
     * @param {OfferFavoriteBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logFavOfferButtonClick(body?: OfferFavoriteBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/fav-offer/`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_has_seen_all_playlist <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenAllPlaylist(body?: AdageBaseModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/playlist`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_has_seen_whole_playlist <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenWholePlaylist(body?: PlaylistBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/has-seen-whole-playlist/`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_header_link_click <POST>
     * @param {AdageHeaderLogBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHeaderLinkClick(body?: AdageHeaderLogBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/header-link-click/`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_offer_details_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferDetailsButtonClick(body?: StockIdBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/offer-detail`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_offer_list_view_switch <POST>
     * @param {OfferListSwitch} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferListViewSwitch(body?: OfferListSwitch, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/offer-list-view-switch`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_offer_template_details_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferTemplateDetailsButtonClick(body?: OfferIdBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/offer-template-detail`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_open_satisfaction_survey <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOpenSatisfactionSurvey(body?: AdageBaseModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/sat-survey`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_request_form_popin_dismiss <POST>
     * @param {CollectiveRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logRequestFormPopinDismiss(body?: CollectiveRequestBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/request-popin-dismiss`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_search_button_click <POST>
     * @param {SearchBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchButtonClick(body?: SearchBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/search-button`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_search_show_more <POST>
     * @param {TrackingShowMoreBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchShowMore(body?: TrackingShowMoreBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/search-show-more`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_tracking_autocomplete_suggestion_click <POST>
     * @param {TrackingAutocompleteSuggestionBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingAutocompleteSuggestionClick(body?: TrackingAutocompleteSuggestionBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/tracking-autocompletion`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_tracking_cta_share <POST>
     * @param {TrackingCTAShareBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingCtaShare(body?: TrackingCTAShareBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/tracking-cta-share`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_tracking_filter <POST>
     * @param {TrackingFilterBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingFilter(body?: TrackingFilterBody, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/tracking-filter`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary log_tracking_map <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingMap(body?: AdageBaseModel, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/logs/tracking-map`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
    /**
     * 
     * @summary new_template_offers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    newTemplateOffersPlaylist(options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/playlists/new_template_offers`
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_collective_offer_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveOfferFavorites(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling postCollectiveOfferFavorites.')
      }
      const localVarPath = `/adage-iframe/collective/offers/{offer_id}/favorites`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary post_collective_template_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveTemplateFavorites(offer_id: number, options: any = {}): ApiRequestOptions {
      // verify required parameter 'offer_id' is not null or undefined
      if (offer_id === null || offer_id === undefined) {
        throw new RequiredError('offer_id','Required parameter offer_id was null or undefined when calling postCollectiveTemplateFavorites.')
      }
      const localVarPath = `/adage-iframe/collective/templates/{offer_id}/favorites`
        .replace(`{${'offer_id'}}`, encodeURIComponent(String(offer_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary save_redactor_preferences <POST>
     * @param {RedactorPreferences} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveRedactorPreferences(body?: RedactorPreferences, options: any = {}): ApiRequestOptions {
      const localVarPath = `/adage-iframe/redactor/preferences`
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication JWTAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

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
     * @summary authenticate <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    authenticate(options?: any): CancelablePromise<AuthenticatedResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).authenticate(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary book_collective_offer <POST>
     * @param {BookCollectiveOfferRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    bookCollectiveOffer(body?: BookCollectiveOfferRequest, options?: any): CancelablePromise<BookCollectiveOfferResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).bookCollectiveOffer(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_adage_jwt_fake_token <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createAdageJwtFakeToken(options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createAdageJwtFakeToken(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary create_collective_request <POST>
     * @param {number} offer_id 
     * @param {PostCollectiveRequestBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveRequest(offer_id: number, body?: PostCollectiveRequestBodyModel, options?: any): CancelablePromise<CollectiveRequestResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).createCollectiveRequest(offer_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOffer(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteFavoriteForCollectiveOffer(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer_template <DELETE>
     * @param {number} offer_template_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOfferTemplate(offer_template_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).deleteFavoriteForCollectiveOfferTemplate(offer_template_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_academies <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAcademies(options?: any): CancelablePromise<AcademiesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getAcademies(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_classroom_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getClassroomPlaylist(options?: any): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getClassroomPlaylist(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_favorites <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveFavorites(options?: any): CancelablePromise<FavoritesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveFavorites(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffer(offer_id: number, options?: any): CancelablePromise<CollectiveOfferResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOffer(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer_template <GET>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplate(offer_id: number, options?: any): CancelablePromise<CollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOfferTemplate(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offer_templates <GET>
     * @param {Array<number>} ids 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplates(ids: Array<number>, options?: any): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOfferTemplates(ids, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_collective_offers_for_my_institution <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffersForMyInstitution(options?: any): CancelablePromise<ListCollectiveOffersResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getCollectiveOffersForMyInstitution(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_educational_institution_with_budget <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutionWithBudget(options?: any): CancelablePromise<EducationalInstitutionWithBudgetResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getEducationalInstitutionWithBudget(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_educational_offers_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersCategories(options?: any): CancelablePromise<CategoriesResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getEducationalOffersCategories(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_educational_offers_formats <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersFormats(options?: any): CancelablePromise<EacFormatsResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getEducationalOffersFormats(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_local_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getLocalOfferersPlaylist(options?: any): CancelablePromise<LocalOfferersPlaylist> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getLocalOfferersPlaylist(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_new_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNewOfferersPlaylist(options?: any): CancelablePromise<LocalOfferersPlaylist> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getNewOfferersPlaylist(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venue_by_id <GET>
     * @param {number} venue_id 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueById(venue_id: number, getRelative?: boolean, options?: any): CancelablePromise<VenueResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenueById(venue_id, getRelative, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary get_venue_by_siret <GET>
     * @param {string} siret 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueBySiret(siret: string, getRelative?: boolean, options?: any): CancelablePromise<VenueResponse> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).getVenueBySiret(siret, getRelative, options)
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
     * @summary log_booking_modal_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logBookingModalButtonClick(body?: StockIdBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logBookingModalButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_catalog_view <POST>
     * @param {CatalogViewBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logCatalogView(body?: CatalogViewBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logCatalogView(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_consult_playlist_element <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logConsultPlaylistElement(body?: PlaylistBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logConsultPlaylistElement(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_contact_modal_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactModalButtonClick(body?: OfferIdBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logContactModalButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_contact_url_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactUrlClick(body?: OfferIdBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logContactUrlClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_fav_offer_button_click <POST>
     * @param {OfferFavoriteBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logFavOfferButtonClick(body?: OfferFavoriteBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logFavOfferButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_has_seen_all_playlist <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenAllPlaylist(body?: AdageBaseModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logHasSeenAllPlaylist(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_has_seen_whole_playlist <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenWholePlaylist(body?: PlaylistBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logHasSeenWholePlaylist(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_header_link_click <POST>
     * @param {AdageHeaderLogBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHeaderLinkClick(body?: AdageHeaderLogBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logHeaderLinkClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_offer_details_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferDetailsButtonClick(body?: StockIdBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logOfferDetailsButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_offer_list_view_switch <POST>
     * @param {OfferListSwitch} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferListViewSwitch(body?: OfferListSwitch, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logOfferListViewSwitch(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_offer_template_details_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferTemplateDetailsButtonClick(body?: OfferIdBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logOfferTemplateDetailsButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_open_satisfaction_survey <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOpenSatisfactionSurvey(body?: AdageBaseModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logOpenSatisfactionSurvey(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_request_form_popin_dismiss <POST>
     * @param {CollectiveRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logRequestFormPopinDismiss(body?: CollectiveRequestBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logRequestFormPopinDismiss(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_search_button_click <POST>
     * @param {SearchBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchButtonClick(body?: SearchBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logSearchButtonClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_search_show_more <POST>
     * @param {TrackingShowMoreBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchShowMore(body?: TrackingShowMoreBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logSearchShowMore(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_tracking_autocomplete_suggestion_click <POST>
     * @param {TrackingAutocompleteSuggestionBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingAutocompleteSuggestionClick(body?: TrackingAutocompleteSuggestionBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logTrackingAutocompleteSuggestionClick(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_tracking_cta_share <POST>
     * @param {TrackingCTAShareBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingCtaShare(body?: TrackingCTAShareBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logTrackingCtaShare(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_tracking_filter <POST>
     * @param {TrackingFilterBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingFilter(body?: TrackingFilterBody, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logTrackingFilter(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary log_tracking_map <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingMap(body?: AdageBaseModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).logTrackingMap(body, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary new_template_offers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    newTemplateOffersPlaylist(options?: any): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).newTemplateOffersPlaylist(options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_collective_offer_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveOfferFavorites(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postCollectiveOfferFavorites(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary post_collective_template_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveTemplateFavorites(offer_id: number, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).postCollectiveTemplateFavorites(offer_id, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary save_redactor_preferences <POST>
     * @param {RedactorPreferences} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveRedactorPreferences(body?: RedactorPreferences, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DefaultApiFetchParamCreator(configuration).saveRedactorPreferences(body, options)
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
     * @summary authenticate <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    authenticate(options?: any) {
      return DefaultApiFp(configuration).authenticate(options)
    },
    /**
     * 
     * @summary book_collective_offer <POST>
     * @param {BookCollectiveOfferRequest} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    bookCollectiveOffer(body?: BookCollectiveOfferRequest, options?: any) {
      return DefaultApiFp(configuration).bookCollectiveOffer(body, options)
    },
    /**
     * 
     * @summary create_adage_jwt_fake_token <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createAdageJwtFakeToken(options?: any) {
      return DefaultApiFp(configuration).createAdageJwtFakeToken(options)
    },
    /**
     * 
     * @summary create_collective_request <POST>
     * @param {number} offer_id 
     * @param {PostCollectiveRequestBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    createCollectiveRequest(offer_id: number, body?: PostCollectiveRequestBodyModel, options?: any) {
      return DefaultApiFp(configuration).createCollectiveRequest(offer_id, body, options)
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer <DELETE>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOffer(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteFavoriteForCollectiveOffer(offer_id, options)
    },
    /**
     * 
     * @summary delete_favorite_for_collective_offer_template <DELETE>
     * @param {number} offer_template_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    deleteFavoriteForCollectiveOfferTemplate(offer_template_id: number, options?: any) {
      return DefaultApiFp(configuration).deleteFavoriteForCollectiveOfferTemplate(offer_template_id, options)
    },
    /**
     * 
     * @summary get_academies <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getAcademies(options?: any) {
      return DefaultApiFp(configuration).getAcademies(options)
    },
    /**
     * 
     * @summary get_classroom_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getClassroomPlaylist(options?: any) {
      return DefaultApiFp(configuration).getClassroomPlaylist(options)
    },
    /**
     * 
     * @summary get_collective_favorites <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveFavorites(options?: any) {
      return DefaultApiFp(configuration).getCollectiveFavorites(options)
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
     * @summary get_collective_offer_templates <GET>
     * @param {Array<number>} ids 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOfferTemplates(ids: Array<number>, options?: any) {
      return DefaultApiFp(configuration).getCollectiveOfferTemplates(ids, options)
    },
    /**
     * 
     * @summary get_collective_offers_for_my_institution <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getCollectiveOffersForMyInstitution(options?: any) {
      return DefaultApiFp(configuration).getCollectiveOffersForMyInstitution(options)
    },
    /**
     * 
     * @summary get_educational_institution_with_budget <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalInstitutionWithBudget(options?: any) {
      return DefaultApiFp(configuration).getEducationalInstitutionWithBudget(options)
    },
    /**
     * 
     * @summary get_educational_offers_categories <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersCategories(options?: any) {
      return DefaultApiFp(configuration).getEducationalOffersCategories(options)
    },
    /**
     * 
     * @summary get_educational_offers_formats <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getEducationalOffersFormats(options?: any) {
      return DefaultApiFp(configuration).getEducationalOffersFormats(options)
    },
    /**
     * 
     * @summary get_local_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getLocalOfferersPlaylist(options?: any) {
      return DefaultApiFp(configuration).getLocalOfferersPlaylist(options)
    },
    /**
     * 
     * @summary get_new_offerers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getNewOfferersPlaylist(options?: any) {
      return DefaultApiFp(configuration).getNewOfferersPlaylist(options)
    },
    /**
     * 
     * @summary get_venue_by_id <GET>
     * @param {number} venue_id 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueById(venue_id: number, getRelative?: boolean, options?: any) {
      return DefaultApiFp(configuration).getVenueById(venue_id, getRelative, options)
    },
    /**
     * 
     * @summary get_venue_by_siret <GET>
     * @param {string} siret 
     * @param {boolean} [getRelative] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getVenueBySiret(siret: string, getRelative?: boolean, options?: any) {
      return DefaultApiFp(configuration).getVenueBySiret(siret, getRelative, options)
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
     * @summary log_booking_modal_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logBookingModalButtonClick(body?: StockIdBody, options?: any) {
      return DefaultApiFp(configuration).logBookingModalButtonClick(body, options)
    },
    /**
     * 
     * @summary log_catalog_view <POST>
     * @param {CatalogViewBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logCatalogView(body?: CatalogViewBody, options?: any) {
      return DefaultApiFp(configuration).logCatalogView(body, options)
    },
    /**
     * 
     * @summary log_consult_playlist_element <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logConsultPlaylistElement(body?: PlaylistBody, options?: any) {
      return DefaultApiFp(configuration).logConsultPlaylistElement(body, options)
    },
    /**
     * 
     * @summary log_contact_modal_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactModalButtonClick(body?: OfferIdBody, options?: any) {
      return DefaultApiFp(configuration).logContactModalButtonClick(body, options)
    },
    /**
     * 
     * @summary log_contact_url_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logContactUrlClick(body?: OfferIdBody, options?: any) {
      return DefaultApiFp(configuration).logContactUrlClick(body, options)
    },
    /**
     * 
     * @summary log_fav_offer_button_click <POST>
     * @param {OfferFavoriteBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logFavOfferButtonClick(body?: OfferFavoriteBody, options?: any) {
      return DefaultApiFp(configuration).logFavOfferButtonClick(body, options)
    },
    /**
     * 
     * @summary log_has_seen_all_playlist <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenAllPlaylist(body?: AdageBaseModel, options?: any) {
      return DefaultApiFp(configuration).logHasSeenAllPlaylist(body, options)
    },
    /**
     * 
     * @summary log_has_seen_whole_playlist <POST>
     * @param {PlaylistBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHasSeenWholePlaylist(body?: PlaylistBody, options?: any) {
      return DefaultApiFp(configuration).logHasSeenWholePlaylist(body, options)
    },
    /**
     * 
     * @summary log_header_link_click <POST>
     * @param {AdageHeaderLogBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logHeaderLinkClick(body?: AdageHeaderLogBody, options?: any) {
      return DefaultApiFp(configuration).logHeaderLinkClick(body, options)
    },
    /**
     * 
     * @summary log_offer_details_button_click <POST>
     * @param {StockIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferDetailsButtonClick(body?: StockIdBody, options?: any) {
      return DefaultApiFp(configuration).logOfferDetailsButtonClick(body, options)
    },
    /**
     * 
     * @summary log_offer_list_view_switch <POST>
     * @param {OfferListSwitch} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferListViewSwitch(body?: OfferListSwitch, options?: any) {
      return DefaultApiFp(configuration).logOfferListViewSwitch(body, options)
    },
    /**
     * 
     * @summary log_offer_template_details_button_click <POST>
     * @param {OfferIdBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOfferTemplateDetailsButtonClick(body?: OfferIdBody, options?: any) {
      return DefaultApiFp(configuration).logOfferTemplateDetailsButtonClick(body, options)
    },
    /**
     * 
     * @summary log_open_satisfaction_survey <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logOpenSatisfactionSurvey(body?: AdageBaseModel, options?: any) {
      return DefaultApiFp(configuration).logOpenSatisfactionSurvey(body, options)
    },
    /**
     * 
     * @summary log_request_form_popin_dismiss <POST>
     * @param {CollectiveRequestBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logRequestFormPopinDismiss(body?: CollectiveRequestBody, options?: any) {
      return DefaultApiFp(configuration).logRequestFormPopinDismiss(body, options)
    },
    /**
     * 
     * @summary log_search_button_click <POST>
     * @param {SearchBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchButtonClick(body?: SearchBody, options?: any) {
      return DefaultApiFp(configuration).logSearchButtonClick(body, options)
    },
    /**
     * 
     * @summary log_search_show_more <POST>
     * @param {TrackingShowMoreBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logSearchShowMore(body?: TrackingShowMoreBody, options?: any) {
      return DefaultApiFp(configuration).logSearchShowMore(body, options)
    },
    /**
     * 
     * @summary log_tracking_autocomplete_suggestion_click <POST>
     * @param {TrackingAutocompleteSuggestionBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingAutocompleteSuggestionClick(body?: TrackingAutocompleteSuggestionBody, options?: any) {
      return DefaultApiFp(configuration).logTrackingAutocompleteSuggestionClick(body, options)
    },
    /**
     * 
     * @summary log_tracking_cta_share <POST>
     * @param {TrackingCTAShareBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingCtaShare(body?: TrackingCTAShareBody, options?: any) {
      return DefaultApiFp(configuration).logTrackingCtaShare(body, options)
    },
    /**
     * 
     * @summary log_tracking_filter <POST>
     * @param {TrackingFilterBody} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingFilter(body?: TrackingFilterBody, options?: any) {
      return DefaultApiFp(configuration).logTrackingFilter(body, options)
    },
    /**
     * 
     * @summary log_tracking_map <POST>
     * @param {AdageBaseModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    logTrackingMap(body?: AdageBaseModel, options?: any) {
      return DefaultApiFp(configuration).logTrackingMap(body, options)
    },
    /**
     * 
     * @summary new_template_offers_playlist <GET>
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    newTemplateOffersPlaylist(options?: any) {
      return DefaultApiFp(configuration).newTemplateOffersPlaylist(options)
    },
    /**
     * 
     * @summary post_collective_offer_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveOfferFavorites(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).postCollectiveOfferFavorites(offer_id, options)
    },
    /**
     * 
     * @summary post_collective_template_favorites <POST>
     * @param {number} offer_id 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    postCollectiveTemplateFavorites(offer_id: number, options?: any) {
      return DefaultApiFp(configuration).postCollectiveTemplateFavorites(offer_id, options)
    },
    /**
     * 
     * @summary save_redactor_preferences <POST>
     * @param {RedactorPreferences} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    saveRedactorPreferences(body?: RedactorPreferences, options?: any) {
      return DefaultApiFp(configuration).saveRedactorPreferences(body, options)
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
   * @summary authenticate <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public authenticate(options?: any) {
    return DefaultApiFp(this.configuration).authenticate(options)
  }

  /**
   * 
   * @summary book_collective_offer <POST>
   * @param {BookCollectiveOfferRequest} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public bookCollectiveOffer(body?: BookCollectiveOfferRequest, options?: any) {
    return DefaultApiFp(this.configuration).bookCollectiveOffer(body, options)
  }

  /**
   * 
   * @summary create_adage_jwt_fake_token <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createAdageJwtFakeToken(options?: any) {
    return DefaultApiFp(this.configuration).createAdageJwtFakeToken(options)
  }

  /**
   * 
   * @summary create_collective_request <POST>
   * @param {number} offer_id 
   * @param {PostCollectiveRequestBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public createCollectiveRequest(offer_id: number, body?: PostCollectiveRequestBodyModel, options?: any) {
    return DefaultApiFp(this.configuration).createCollectiveRequest(offer_id, body, options)
  }

  /**
   * 
   * @summary delete_favorite_for_collective_offer <DELETE>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteFavoriteForCollectiveOffer(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteFavoriteForCollectiveOffer(offer_id, options)
  }

  /**
   * 
   * @summary delete_favorite_for_collective_offer_template <DELETE>
   * @param {number} offer_template_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public deleteFavoriteForCollectiveOfferTemplate(offer_template_id: number, options?: any) {
    return DefaultApiFp(this.configuration).deleteFavoriteForCollectiveOfferTemplate(offer_template_id, options)
  }

  /**
   * 
   * @summary get_academies <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getAcademies(options?: any) {
    return DefaultApiFp(this.configuration).getAcademies(options)
  }

  /**
   * 
   * @summary get_classroom_playlist <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getClassroomPlaylist(options?: any) {
    return DefaultApiFp(this.configuration).getClassroomPlaylist(options)
  }

  /**
   * 
   * @summary get_collective_favorites <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveFavorites(options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveFavorites(options)
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
   * @summary get_collective_offer_templates <GET>
   * @param {Array<number>} ids 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOfferTemplates(ids: Array<number>, options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOfferTemplates(ids, options)
  }

  /**
   * 
   * @summary get_collective_offers_for_my_institution <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getCollectiveOffersForMyInstitution(options?: any) {
    return DefaultApiFp(this.configuration).getCollectiveOffersForMyInstitution(options)
  }

  /**
   * 
   * @summary get_educational_institution_with_budget <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getEducationalInstitutionWithBudget(options?: any) {
    return DefaultApiFp(this.configuration).getEducationalInstitutionWithBudget(options)
  }

  /**
   * 
   * @summary get_educational_offers_categories <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getEducationalOffersCategories(options?: any) {
    return DefaultApiFp(this.configuration).getEducationalOffersCategories(options)
  }

  /**
   * 
   * @summary get_educational_offers_formats <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getEducationalOffersFormats(options?: any) {
    return DefaultApiFp(this.configuration).getEducationalOffersFormats(options)
  }

  /**
   * 
   * @summary get_local_offerers_playlist <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getLocalOfferersPlaylist(options?: any) {
    return DefaultApiFp(this.configuration).getLocalOfferersPlaylist(options)
  }

  /**
   * 
   * @summary get_new_offerers_playlist <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getNewOfferersPlaylist(options?: any) {
    return DefaultApiFp(this.configuration).getNewOfferersPlaylist(options)
  }

  /**
   * 
   * @summary get_venue_by_id <GET>
   * @param {number} venue_id 
   * @param {boolean} [getRelative] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenueById(venue_id: number, getRelative?: boolean, options?: any) {
    return DefaultApiFp(this.configuration).getVenueById(venue_id, getRelative, options)
  }

  /**
   * 
   * @summary get_venue_by_siret <GET>
   * @param {string} siret 
   * @param {boolean} [getRelative] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public getVenueBySiret(siret: string, getRelative?: boolean, options?: any) {
    return DefaultApiFp(this.configuration).getVenueBySiret(siret, getRelative, options)
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
   * @summary log_booking_modal_button_click <POST>
   * @param {StockIdBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logBookingModalButtonClick(body?: StockIdBody, options?: any) {
    return DefaultApiFp(this.configuration).logBookingModalButtonClick(body, options)
  }

  /**
   * 
   * @summary log_catalog_view <POST>
   * @param {CatalogViewBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logCatalogView(body?: CatalogViewBody, options?: any) {
    return DefaultApiFp(this.configuration).logCatalogView(body, options)
  }

  /**
   * 
   * @summary log_consult_playlist_element <POST>
   * @param {PlaylistBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logConsultPlaylistElement(body?: PlaylistBody, options?: any) {
    return DefaultApiFp(this.configuration).logConsultPlaylistElement(body, options)
  }

  /**
   * 
   * @summary log_contact_modal_button_click <POST>
   * @param {OfferIdBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logContactModalButtonClick(body?: OfferIdBody, options?: any) {
    return DefaultApiFp(this.configuration).logContactModalButtonClick(body, options)
  }

  /**
   * 
   * @summary log_contact_url_click <POST>
   * @param {OfferIdBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logContactUrlClick(body?: OfferIdBody, options?: any) {
    return DefaultApiFp(this.configuration).logContactUrlClick(body, options)
  }

  /**
   * 
   * @summary log_fav_offer_button_click <POST>
   * @param {OfferFavoriteBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logFavOfferButtonClick(body?: OfferFavoriteBody, options?: any) {
    return DefaultApiFp(this.configuration).logFavOfferButtonClick(body, options)
  }

  /**
   * 
   * @summary log_has_seen_all_playlist <POST>
   * @param {AdageBaseModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logHasSeenAllPlaylist(body?: AdageBaseModel, options?: any) {
    return DefaultApiFp(this.configuration).logHasSeenAllPlaylist(body, options)
  }

  /**
   * 
   * @summary log_has_seen_whole_playlist <POST>
   * @param {PlaylistBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logHasSeenWholePlaylist(body?: PlaylistBody, options?: any) {
    return DefaultApiFp(this.configuration).logHasSeenWholePlaylist(body, options)
  }

  /**
   * 
   * @summary log_header_link_click <POST>
   * @param {AdageHeaderLogBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logHeaderLinkClick(body?: AdageHeaderLogBody, options?: any) {
    return DefaultApiFp(this.configuration).logHeaderLinkClick(body, options)
  }

  /**
   * 
   * @summary log_offer_details_button_click <POST>
   * @param {StockIdBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logOfferDetailsButtonClick(body?: StockIdBody, options?: any) {
    return DefaultApiFp(this.configuration).logOfferDetailsButtonClick(body, options)
  }

  /**
   * 
   * @summary log_offer_list_view_switch <POST>
   * @param {OfferListSwitch} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logOfferListViewSwitch(body?: OfferListSwitch, options?: any) {
    return DefaultApiFp(this.configuration).logOfferListViewSwitch(body, options)
  }

  /**
   * 
   * @summary log_offer_template_details_button_click <POST>
   * @param {OfferIdBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logOfferTemplateDetailsButtonClick(body?: OfferIdBody, options?: any) {
    return DefaultApiFp(this.configuration).logOfferTemplateDetailsButtonClick(body, options)
  }

  /**
   * 
   * @summary log_open_satisfaction_survey <POST>
   * @param {AdageBaseModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logOpenSatisfactionSurvey(body?: AdageBaseModel, options?: any) {
    return DefaultApiFp(this.configuration).logOpenSatisfactionSurvey(body, options)
  }

  /**
   * 
   * @summary log_request_form_popin_dismiss <POST>
   * @param {CollectiveRequestBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logRequestFormPopinDismiss(body?: CollectiveRequestBody, options?: any) {
    return DefaultApiFp(this.configuration).logRequestFormPopinDismiss(body, options)
  }

  /**
   * 
   * @summary log_search_button_click <POST>
   * @param {SearchBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logSearchButtonClick(body?: SearchBody, options?: any) {
    return DefaultApiFp(this.configuration).logSearchButtonClick(body, options)
  }

  /**
   * 
   * @summary log_search_show_more <POST>
   * @param {TrackingShowMoreBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logSearchShowMore(body?: TrackingShowMoreBody, options?: any) {
    return DefaultApiFp(this.configuration).logSearchShowMore(body, options)
  }

  /**
   * 
   * @summary log_tracking_autocomplete_suggestion_click <POST>
   * @param {TrackingAutocompleteSuggestionBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logTrackingAutocompleteSuggestionClick(body?: TrackingAutocompleteSuggestionBody, options?: any) {
    return DefaultApiFp(this.configuration).logTrackingAutocompleteSuggestionClick(body, options)
  }

  /**
   * 
   * @summary log_tracking_cta_share <POST>
   * @param {TrackingCTAShareBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logTrackingCtaShare(body?: TrackingCTAShareBody, options?: any) {
    return DefaultApiFp(this.configuration).logTrackingCtaShare(body, options)
  }

  /**
   * 
   * @summary log_tracking_filter <POST>
   * @param {TrackingFilterBody} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logTrackingFilter(body?: TrackingFilterBody, options?: any) {
    return DefaultApiFp(this.configuration).logTrackingFilter(body, options)
  }

  /**
   * 
   * @summary log_tracking_map <POST>
   * @param {AdageBaseModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public logTrackingMap(body?: AdageBaseModel, options?: any) {
    return DefaultApiFp(this.configuration).logTrackingMap(body, options)
  }

  /**
   * 
   * @summary new_template_offers_playlist <GET>
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public newTemplateOffersPlaylist(options?: any) {
    return DefaultApiFp(this.configuration).newTemplateOffersPlaylist(options)
  }

  /**
   * 
   * @summary post_collective_offer_favorites <POST>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postCollectiveOfferFavorites(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).postCollectiveOfferFavorites(offer_id, options)
  }

  /**
   * 
   * @summary post_collective_template_favorites <POST>
   * @param {number} offer_id 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public postCollectiveTemplateFavorites(offer_id: number, options?: any) {
    return DefaultApiFp(this.configuration).postCollectiveTemplateFavorites(offer_id, options)
  }

  /**
   * 
   * @summary save_redactor_preferences <POST>
   * @param {RedactorPreferences} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DefaultApi
   */
  public saveRedactorPreferences(body?: RedactorPreferences, options?: any) {
    return DefaultApiFp(this.configuration).saveRedactorPreferences(body, options)
  }

}
