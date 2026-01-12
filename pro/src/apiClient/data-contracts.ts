/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/**
 * WithdrawalTypeEnum
 * An enumeration.
 */
export enum WithdrawalTypeEnum {
  ByEmail = 'by_email',
  InApp = 'in_app',
  NoTicket = 'no_ticket',
  OnSite = 'on_site',
}

/**
 * VenueTypeCode
 * An enumeration.
 */
export enum VenueTypeCode {
  Autre = 'Autre',
  ArtsVisuelsArtsPlastiquesEtGaleries = 'Arts visuels, arts plastiques et galeries',
  BibliothequeOuMediatheque = 'Bibliothèque ou médiathèque',
  CentreCulturel = 'Centre culturel',
  CinemaSalleDeProjections = 'Cinéma - Salle de projections',
  CinemaItinerant = 'Cinéma itinérant',
  CoursEtPratiqueArtistiques = 'Cours et pratique artistiques',
  CultureScientifique = 'Culture scientifique',
  Festival = 'Festival',
  JeuxJeuxVideos = 'Jeux / Jeux vidéos',
  Librairie = 'Librairie',
  MagasinArtsCreatifs = 'Magasin arts créatifs',
  MagasinDeDistributionDeProduitsCulturels = 'Magasin de distribution de produits culturels',
  MusiqueDisquaire = 'Musique - Disquaire',
  MusiqueMagasinDinstruments = 'Musique - Magasin d’instruments',
  MusiqueSalleDeConcerts = 'Musique - Salle de concerts',
  Musee = 'Musée',
  OffreNumerique = 'Offre numérique',
  PatrimoineEtTourisme = 'Patrimoine et tourisme',
  SpectacleVivant = 'Spectacle vivant',
}

/** UserRole */
export enum UserRole {
  ADMIN = 'ADMIN',
  ANONYMIZED = 'ANONYMIZED',
  BENEFICIARY = 'BENEFICIARY',
  UNDERAGE_BENEFICIARY = 'UNDERAGE_BENEFICIARY',
  FREE_BENEFICIARY = 'FREE_BENEFICIARY',
  PRO = 'PRO',
  NON_ATTACHED_PRO = 'NON_ATTACHED_PRO',
  TEST = 'TEST',
}

/**
 * Target
 * An enumeration.
 */
export enum Target {
  EDUCATIONAL = 'EDUCATIONAL',
  INDIVIDUAL_AND_EDUCATIONAL = 'INDIVIDUAL_AND_EDUCATIONAL',
  INDIVIDUAL = 'INDIVIDUAL',
}

/**
 * SubcategoryIdEnum
 * An enumeration.
 */
export enum SubcategoryIdEnum {
  ABO_BIBLIOTHEQUE = 'ABO_BIBLIOTHEQUE',
  ABO_CONCERT = 'ABO_CONCERT',
  ABO_JEU_VIDEO = 'ABO_JEU_VIDEO',
  ABO_LIVRE_NUMERIQUE = 'ABO_LIVRE_NUMERIQUE',
  ABO_LUDOTHEQUE = 'ABO_LUDOTHEQUE',
  ABO_MEDIATHEQUE = 'ABO_MEDIATHEQUE',
  ABO_PLATEFORME_MUSIQUE = 'ABO_PLATEFORME_MUSIQUE',
  ABO_PLATEFORME_VIDEO = 'ABO_PLATEFORME_VIDEO',
  ABO_PRATIQUE_ART = 'ABO_PRATIQUE_ART',
  ABO_PRESSE_EN_LIGNE = 'ABO_PRESSE_EN_LIGNE',
  ABO_SPECTACLE = 'ABO_SPECTACLE',
  ACHAT_INSTRUMENT = 'ACHAT_INSTRUMENT',
  ACTIVATION_EVENT = 'ACTIVATION_EVENT',
  ACTIVATION_THING = 'ACTIVATION_THING',
  APP_CULTURELLE = 'APP_CULTURELLE',
  ATELIER_PRATIQUE_ART = 'ATELIER_PRATIQUE_ART',
  AUTRE_SUPPORT_NUMERIQUE = 'AUTRE_SUPPORT_NUMERIQUE',
  BON_ACHAT_INSTRUMENT = 'BON_ACHAT_INSTRUMENT',
  CAPTATION_MUSIQUE = 'CAPTATION_MUSIQUE',
  CARTE_CINE_ILLIMITE = 'CARTE_CINE_ILLIMITE',
  CARTE_CINE_MULTISEANCES = 'CARTE_CINE_MULTISEANCES',
  CARTE_JEUNES = 'CARTE_JEUNES',
  CARTE_MUSEE = 'CARTE_MUSEE',
  CINE_PLEIN_AIR = 'CINE_PLEIN_AIR',
  CINE_VENTE_DISTANCE = 'CINE_VENTE_DISTANCE',
  CONCERT = 'CONCERT',
  CONCOURS = 'CONCOURS',
  CONFERENCE = 'CONFERENCE',
  DECOUVERTE_METIERS = 'DECOUVERTE_METIERS',
  ESCAPE_GAME = 'ESCAPE_GAME',
  EVENEMENT_CINE = 'EVENEMENT_CINE',
  EVENEMENT_JEU = 'EVENEMENT_JEU',
  EVENEMENT_MUSIQUE = 'EVENEMENT_MUSIQUE',
  EVENEMENT_PATRIMOINE = 'EVENEMENT_PATRIMOINE',
  FESTIVAL_ART_VISUEL = 'FESTIVAL_ART_VISUEL',
  FESTIVAL_CINE = 'FESTIVAL_CINE',
  FESTIVAL_LIVRE = 'FESTIVAL_LIVRE',
  FESTIVAL_MUSIQUE = 'FESTIVAL_MUSIQUE',
  FESTIVAL_SPECTACLE = 'FESTIVAL_SPECTACLE',
  JEU_EN_LIGNE = 'JEU_EN_LIGNE',
  JEU_SUPPORT_PHYSIQUE = 'JEU_SUPPORT_PHYSIQUE',
  LIVESTREAM_EVENEMENT = 'LIVESTREAM_EVENEMENT',
  LIVESTREAM_MUSIQUE = 'LIVESTREAM_MUSIQUE',
  LIVESTREAM_PRATIQUE_ARTISTIQUE = 'LIVESTREAM_PRATIQUE_ARTISTIQUE',
  LIVRE_AUDIO_PHYSIQUE = 'LIVRE_AUDIO_PHYSIQUE',
  LIVRE_NUMERIQUE = 'LIVRE_NUMERIQUE',
  LIVRE_PAPIER = 'LIVRE_PAPIER',
  LOCATION_INSTRUMENT = 'LOCATION_INSTRUMENT',
  MATERIEL_ART_CREATIF = 'MATERIEL_ART_CREATIF',
  MUSEE_VENTE_DISTANCE = 'MUSEE_VENTE_DISTANCE',
  OEUVRE_ART = 'OEUVRE_ART',
  PARTITION = 'PARTITION',
  PLATEFORME_PRATIQUE_ARTISTIQUE = 'PLATEFORME_PRATIQUE_ARTISTIQUE',
  PRATIQUE_ART_VENTE_DISTANCE = 'PRATIQUE_ART_VENTE_DISTANCE',
  PODCAST = 'PODCAST',
  RENCONTRE_EN_LIGNE = 'RENCONTRE_EN_LIGNE',
  RENCONTRE_JEU = 'RENCONTRE_JEU',
  RENCONTRE = 'RENCONTRE',
  SALON = 'SALON',
  SEANCE_CINE = 'SEANCE_CINE',
  SEANCE_ESSAI_PRATIQUE_ART = 'SEANCE_ESSAI_PRATIQUE_ART',
  SPECTACLE_ENREGISTRE = 'SPECTACLE_ENREGISTRE',
  SPECTACLE_REPRESENTATION = 'SPECTACLE_REPRESENTATION',
  SPECTACLE_VENTE_DISTANCE = 'SPECTACLE_VENTE_DISTANCE',
  SUPPORT_PHYSIQUE_FILM = 'SUPPORT_PHYSIQUE_FILM',
  SUPPORT_PHYSIQUE_MUSIQUE_CD = 'SUPPORT_PHYSIQUE_MUSIQUE_CD',
  SUPPORT_PHYSIQUE_MUSIQUE_VINYLE = 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
  TELECHARGEMENT_LIVRE_AUDIO = 'TELECHARGEMENT_LIVRE_AUDIO',
  TELECHARGEMENT_MUSIQUE = 'TELECHARGEMENT_MUSIQUE',
  VISITE_GUIDEE = 'VISITE_GUIDEE',
  VISITE_VIRTUELLE = 'VISITE_VIRTUELLE',
  VISITE = 'VISITE',
  VOD = 'VOD',
}

/**
 * StudentLevels
 * An enumeration.
 */
export enum StudentLevels {
  ValueEcolesMarseilleMaternelle = 'Écoles Marseille - Maternelle',
  ValueEcolesMarseilleCPCE1CE2 = 'Écoles Marseille - CP, CE1, CE2',
  ValueEcolesMarseilleCM1CM2 = 'Écoles Marseille - CM1, CM2',
  College6E = 'Collège - 6e',
  College5E = 'Collège - 5e',
  College4E = 'Collège - 4e',
  College3E = 'Collège - 3e',
  LyceeSeconde = 'Lycée - Seconde',
  LyceePremiere = 'Lycée - Première',
  LyceeTerminale = 'Lycée - Terminale',
  CAP2EAnnee = 'CAP - 2e année',
  CAP1ReAnnee = 'CAP - 1re année',
}

/**
 * StocksOrderedBy
 * An enumeration.
 */
export enum StocksOrderedBy {
  DATE = 'DATE',
  TIME = 'TIME',
  BEGINNING_DATETIME = 'BEGINNING_DATETIME',
  PRICE_CATEGORY_ID = 'PRICE_CATEGORY_ID',
  BOOKING_LIMIT_DATETIME = 'BOOKING_LIMIT_DATETIME',
  REMAINING_QUANTITY = 'REMAINING_QUANTITY',
  DN_BOOKED_QUANTITY = 'DN_BOOKED_QUANTITY',
}

/**
 * SimplifiedBankAccountStatus
 * An enumeration.
 */
export enum SimplifiedBankAccountStatus {
  Pending = 'pending',
  Valid = 'valid',
  PendingCorrections = 'pending_corrections',
}

/** PhoneValidationStatusType */
export enum PhoneValidationStatusType {
  SkippedBySupport = 'skipped-by-support',
  Unvalidated = 'unvalidated',
  Validated = 'validated',
}

/**
 * OffererMemberStatus
 * An enumeration.
 */
export enum OffererMemberStatus {
  Validated = 'validated',
  Pending = 'pending',
}

/**
 * OfferStatus
 * An enumeration.
 */
export enum OfferStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  REJECTED = 'REJECTED',
  INACTIVE = 'INACTIVE',
  SCHEDULED = 'SCHEDULED',
  PUBLISHED = 'PUBLISHED',
  ACTIVE = 'ACTIVE',
  SOLD_OUT = 'SOLD_OUT',
  EXPIRED = 'EXPIRED',
}

/**
 * OfferContactFormEnum
 * An enumeration.
 */
export enum OfferContactFormEnum {
  Form = 'form',
}

/**
 * GetOffererAddressesWithOffersOption
 * An enumeration.
 */
export enum GetOffererAddressesWithOffersOption {
  INDIVIDUAL_OFFERS_ONLY = 'INDIVIDUAL_OFFERS_ONLY',
  COLLECTIVE_OFFERS_ONLY = 'COLLECTIVE_OFFERS_ONLY',
  COLLECTIVE_OFFER_TEMPLATES_ONLY = 'COLLECTIVE_OFFER_TEMPLATES_ONLY',
}

/** GenderEnum */
export enum GenderEnum {
  M = 'M.',
  Mme = 'Mme',
}

/**
 * EacFormat
 * An enumeration.
 */
export enum EacFormat {
  AtelierDePratique = 'Atelier de pratique',
  Concert = 'Concert',
  ConferenceRencontre = 'Conférence, rencontre',
  FestivalSalonCongres = 'Festival, salon, congrès',
  ProjectionAudiovisuelle = 'Projection audiovisuelle',
  Representation = 'Représentation',
  VisiteGuidee = 'Visite guidée',
  VisiteLibre = 'Visite libre',
}

/**
 * DisplayableActivity
 * An enumeration.
 */
export enum DisplayableActivity {
  ART_GALLERY = 'ART_GALLERY',
  ART_SCHOOL = 'ART_SCHOOL',
  ARTISTIC_COMPANY = 'ARTISTIC_COMPANY',
  ARTS_CENTRE = 'ARTS_CENTRE',
  ARTS_EDUCATION = 'ARTS_EDUCATION',
  BOOKSTORE = 'BOOKSTORE',
  CINEMA = 'CINEMA',
  COMMUNITY_CENTRE = 'COMMUNITY_CENTRE',
  CREATIVE_ARTS_STORE = 'CREATIVE_ARTS_STORE',
  CULTURAL_CENTRE = 'CULTURAL_CENTRE',
  CULTURAL_MEDIATION = 'CULTURAL_MEDIATION',
  DISTRIBUTION_STORE = 'DISTRIBUTION_STORE',
  FESTIVAL = 'FESTIVAL',
  GAMES_CENTRE = 'GAMES_CENTRE',
  HERITAGE_SITE = 'HERITAGE_SITE',
  LIBRARY = 'LIBRARY',
  MUSEUM = 'MUSEUM',
  MUSIC_INSTRUMENT_STORE = 'MUSIC_INSTRUMENT_STORE',
  OTHER = 'OTHER',
  PERFORMANCE_HALL = 'PERFORMANCE_HALL',
  PRESS = 'PRESS',
  PRODUCTION_OR_PROMOTION_COMPANY = 'PRODUCTION_OR_PROMOTION_COMPANY',
  RECORD_STORE = 'RECORD_STORE',
  SCIENCE_CENTRE = 'SCIENCE_CENTRE',
  STREAMING_PLATFORM = 'STREAMING_PLATFORM',
  TOURIST_INFORMATION_CENTRE = 'TOURIST_INFORMATION_CENTRE',
  TRAVELLING_CINEMA = 'TRAVELLING_CINEMA',
}

/**
 * DMSApplicationstatus
 * An enumeration.
 */
export enum DMSApplicationstatus {
  Accepte = 'accepte',
  SansSuite = 'sans_suite',
  EnConstruction = 'en_construction',
  Refuse = 'refuse',
  EnInstruction = 'en_instruction',
}

/**
 * CollectiveOfferTemplateAllowedAction
 * An enumeration.
 */
export enum CollectiveOfferTemplateAllowedAction {
  CAN_EDIT_DETAILS = 'CAN_EDIT_DETAILS',
  CAN_DUPLICATE = 'CAN_DUPLICATE',
  CAN_ARCHIVE = 'CAN_ARCHIVE',
  CAN_CREATE_BOOKABLE_OFFER = 'CAN_CREATE_BOOKABLE_OFFER',
  CAN_PUBLISH = 'CAN_PUBLISH',
  CAN_HIDE = 'CAN_HIDE',
  CAN_SHARE = 'CAN_SHARE',
}

/**
 * CollectiveOfferDisplayedStatus
 * An enumeration.
 */
export enum CollectiveOfferDisplayedStatus {
  PUBLISHED = 'PUBLISHED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  REJECTED = 'REJECTED',
  PREBOOKED = 'PREBOOKED',
  BOOKED = 'BOOKED',
  HIDDEN = 'HIDDEN',
  EXPIRED = 'EXPIRED',
  ENDED = 'ENDED',
  CANCELLED = 'CANCELLED',
  REIMBURSED = 'REIMBURSED',
  ARCHIVED = 'ARCHIVED',
  DRAFT = 'DRAFT',
}

/**
 * CollectiveOfferAllowedAction
 * An enumeration.
 */
export enum CollectiveOfferAllowedAction {
  CAN_EDIT_DETAILS = 'CAN_EDIT_DETAILS',
  CAN_EDIT_DATES = 'CAN_EDIT_DATES',
  CAN_EDIT_INSTITUTION = 'CAN_EDIT_INSTITUTION',
  CAN_EDIT_DISCOUNT = 'CAN_EDIT_DISCOUNT',
  CAN_DUPLICATE = 'CAN_DUPLICATE',
  CAN_CANCEL = 'CAN_CANCEL',
  CAN_ARCHIVE = 'CAN_ARCHIVE',
}

/**
 * CollectiveLocationType
 * An enumeration.
 */
export enum CollectiveLocationType {
  SCHOOL = 'SCHOOL',
  ADDRESS = 'ADDRESS',
  TO_BE_DEFINED = 'TO_BE_DEFINED',
}

/**
 * CollectiveBookingStatus
 * An enumeration.
 */
export enum CollectiveBookingStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  USED = 'USED',
  CANCELLED = 'CANCELLED',
  REIMBURSED = 'REIMBURSED',
}

/**
 * CollectiveBookingCancellationReasons
 * An enumeration.
 */
export enum CollectiveBookingCancellationReasons {
  OFFERER = 'OFFERER',
  BENEFICIARY = 'BENEFICIARY',
  EXPIRED = 'EXPIRED',
  FRAUD = 'FRAUD',
  FRAUD_SUSPICION = 'FRAUD_SUSPICION',
  FRAUD_INAPPROPRIATE = 'FRAUD_INAPPROPRIATE',
  REFUSED_BY_INSTITUTE = 'REFUSED_BY_INSTITUTE',
  REFUSED_BY_HEADMASTER = 'REFUSED_BY_HEADMASTER',
  PUBLIC_API = 'PUBLIC_API',
  FINANCE_INCIDENT = 'FINANCE_INCIDENT',
  BACKOFFICE = 'BACKOFFICE',
  BACKOFFICE_EVENT_CANCELLED = 'BACKOFFICE_EVENT_CANCELLED',
  BACKOFFICE_OFFER_MODIFIED = 'BACKOFFICE_OFFER_MODIFIED',
  BACKOFFICE_OFFER_WITH_WRONG_INFORMATION = 'BACKOFFICE_OFFER_WITH_WRONG_INFORMATION',
  BACKOFFICE_OFFERER_BUSINESS_CLOSED = 'BACKOFFICE_OFFERER_BUSINESS_CLOSED',
  OFFERER_CONNECT_AS = 'OFFERER_CONNECT_AS',
  OFFERER_CLOSED = 'OFFERER_CLOSED',
}

/** BookingsExportStatusFilter */
export enum BookingsExportStatusFilter {
  Validated = 'validated',
  All = 'all',
}

/** BookingStatusFilter */
export enum BookingStatusFilter {
  Booked = 'booked',
  Validated = 'validated',
  Reimbursed = 'reimbursed',
}

/** BookingRecapStatus */
export enum BookingRecapStatus {
  Booked = 'booked',
  Validated = 'validated',
  Cancelled = 'cancelled',
  Reimbursed = 'reimbursed',
  Confirmed = 'confirmed',
  Pending = 'pending',
}

/** BookingOfferType */
export enum BookingOfferType {
  BIEN = 'BIEN',
  EVENEMENT = 'EVENEMENT',
}

/** BookingExportType */
export enum BookingExportType {
  Csv = 'csv',
  Excel = 'excel',
}

/** BankAccountApplicationStatus */
export enum BankAccountApplicationStatus {
  EnConstruction = 'en_construction',
  EnInstruction = 'en_instruction',
  Accepte = 'accepte',
  Refuse = 'refuse',
  SansSuite = 'sans_suite',
  ACorriger = 'a_corriger',
}

/**
 * ArtistType
 * A link Artist <> Product also bears a type
 * An artist can be an author or a musician for different products
 */
export enum ArtistType {
  Author = 'author',
  Performer = 'performer',
  StageDirector = 'stage_director',
}

/**
 * ActivityOpenToPublic
 * An enumeration.
 */
export enum ActivityOpenToPublic {
  ART_GALLERY = 'ART_GALLERY',
  ART_SCHOOL = 'ART_SCHOOL',
  ARTS_CENTRE = 'ARTS_CENTRE',
  BOOKSTORE = 'BOOKSTORE',
  CINEMA = 'CINEMA',
  COMMUNITY_CENTRE = 'COMMUNITY_CENTRE',
  CREATIVE_ARTS_STORE = 'CREATIVE_ARTS_STORE',
  CULTURAL_CENTRE = 'CULTURAL_CENTRE',
  DISTRIBUTION_STORE = 'DISTRIBUTION_STORE',
  FESTIVAL = 'FESTIVAL',
  HERITAGE_SITE = 'HERITAGE_SITE',
  LIBRARY = 'LIBRARY',
  MUSEUM = 'MUSEUM',
  MUSIC_INSTRUMENT_STORE = 'MUSIC_INSTRUMENT_STORE',
  OTHER = 'OTHER',
  PERFORMANCE_HALL = 'PERFORMANCE_HALL',
  RECORD_STORE = 'RECORD_STORE',
  SCIENCE_CENTRE = 'SCIENCE_CENTRE',
  TOURIST_INFORMATION_CENTRE = 'TOURIST_INFORMATION_CENTRE',
}

/**
 * ActivityNotOpenToPublic
 * An enumeration.
 */
export enum ActivityNotOpenToPublic {
  ARTISTIC_COMPANY = 'ARTISTIC_COMPANY',
  ARTS_EDUCATION = 'ARTS_EDUCATION',
  CULTURAL_MEDIATION = 'CULTURAL_MEDIATION',
  FESTIVAL = 'FESTIVAL',
  OTHER = 'OTHER',
  PRESS = 'PRESS',
  PRODUCTION_OR_PROMOTION_COMPANY = 'PRODUCTION_OR_PROMOTION_COMPANY',
  STREAMING_PLATFORM = 'STREAMING_PLATFORM',
  TRAVELLING_CINEMA = 'TRAVELLING_CINEMA',
}

/** AggregatedRevenueModel */
export interface AggregatedRevenueModel {
  /**
   * Expectedrevenue
   * @default null
   */
  expectedRevenue?: CollectiveRevenue | IndividualRevenue | TotalRevenue | null
  /** Revenue */
  revenue: CollectiveRevenue | IndividualRevenue | TotalRevenue
}

/** ArtistOfferResponseModel */
export interface ArtistOfferResponseModel {
  /** Artistid */
  artistId: string | null
  /**
   * A link Artist <> Product also bears a type
   * An artist can be an author or a musician for different products
   */
  artistType: ArtistType
  /** Customname */
  customName: string | null
}

/** ArtistQueryModel */
export interface ArtistQueryModel {
  /** Search */
  search: string
}

/** ArtistResponseModel */
export interface ArtistResponseModel {
  /** Id */
  id: string
  /** Name */
  name: string
  /** Thumburl */
  thumbUrl: string | null
}

/** ArtistsResponseModel */
export type ArtistsResponseModel = ArtistResponseModel[]

/** AttachImageFormModel */
export interface AttachImageFormModel {
  /** Credit */
  credit: string
  /** Croppingrectheight */
  croppingRectHeight: number
  /** Croppingrectwidth */
  croppingRectWidth: number
  /** Croppingrectx */
  croppingRectX: number
  /** Croppingrecty */
  croppingRectY: number
}

/** AttachImageResponseModel */
export interface AttachImageResponseModel {
  /** Imageurl */
  imageUrl: string
}

/** AudioDisabilityModel */
export interface AudioDisabilityModel {
  /**
   * Deafandhardofhearing
   * @default ["Non renseigné"]
   */
  deafAndHardOfHearing?: string[]
}

/** BankAccountResponseModel */
export interface BankAccountResponseModel {
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** Dsapplicationid */
  dsApplicationId: number | null
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Label */
  label: string
  /** Linkedvenues */
  linkedVenues: LinkedVenue[]
  /** Obfuscatediban */
  obfuscatedIban: string
  status: BankAccountApplicationStatus
}

/** BannerMetaModel */
export interface BannerMetaModel {
  /**
   * Crop Params
   * @default {"height_crop_percent":1,"width_crop_percent":1,"x_crop_percent":0,"y_crop_percent":0}
   */
  crop_params?: CropParams
  /**
   * Image Credit
   * @minLength 1
   * @maxLength 255
   */
  image_credit?: string | null
  /** Original Image Url */
  original_image_url?: string | null
}

/** BookingRecapResponseBeneficiaryModel */
export interface BookingRecapResponseBeneficiaryModel {
  /**
   * Email
   * @default null
   */
  email?: string | null
  /**
   * Firstname
   * @default null
   */
  firstname?: string | null
  /**
   * Lastname
   * @default null
   */
  lastname?: string | null
  /**
   * Phonenumber
   * @default null
   */
  phonenumber?: string | null
}

/** BookingRecapResponseBookingStatusHistoryModel */
export interface BookingRecapResponseBookingStatusHistoryModel {
  /**
   * Date
   * @default null
   */
  date?: string | null
  status: BookingRecapStatus
}

/** BookingRecapResponseModel */
export interface BookingRecapResponseModel {
  beneficiary: BookingRecapResponseBeneficiaryModel
  /** Bookingamount */
  bookingAmount: number
  /**
   * Bookingdate
   * @format date-time
   */
  bookingDate: string
  /** Bookingisduo */
  bookingIsDuo: boolean
  /**
   * Bookingpricecategorylabel
   * @default null
   */
  bookingPriceCategoryLabel?: string | null
  bookingStatus: BookingRecapStatus
  /** Bookingstatushistory */
  bookingStatusHistory: BookingRecapResponseBookingStatusHistoryModel[]
  /**
   * Bookingtoken
   * @default null
   */
  bookingToken?: string | null
  stock: BookingRecapResponseStockModel
}

/** BookingRecapResponseStockModel */
export interface BookingRecapResponseStockModel {
  /**
   * Eventbeginningdatetime
   * @default null
   */
  eventBeginningDatetime?: string | null
  /**
   * Offerean
   * @default null
   */
  offerEan?: string | null
  /** Offerid */
  offerId: number
  /** Offeriseducational */
  offerIsEducational: boolean
  /** Offername */
  offerName: string
}

/** BookingsExportQueryModel */
export interface BookingsExportQueryModel {
  /**
   * Eventdate
   * @format date
   */
  eventDate: string
  status: BookingsExportStatusFilter
}

/** CategoriesResponseModel */
export interface CategoriesResponseModel {
  /** Categories */
  categories: CategoryResponseModel[]
  /** Subcategories */
  subcategories: SubcategoryResponseModel[]
}

/** CategoryResponseModel */
export interface CategoryResponseModel {
  /** Id */
  id: string
  /** Isselectable */
  isSelectable: boolean
  /** Prolabel */
  proLabel: string
}

/** ChangePasswordBodyModel */
export interface ChangePasswordBodyModel {
  /** Newconfirmationpassword */
  newConfirmationPassword: string
  /** Newpassword */
  newPassword: string
  /** Oldpassword */
  oldPassword: string
}

/** ChangeProEmailBody */
export interface ChangeProEmailBody {
  /** Token */
  token: string
}

/** CheckTokenBodyModel */
export interface CheckTokenBodyModel {
  /**
   * Token
   * @minLength 1
   */
  token: string
}

/** CollectiveOfferDatesModel */
export interface CollectiveOfferDatesModel {
  /**
   * End
   * @format date-time
   */
  end: string
  /**
   * Start
   * @format date-time
   */
  start: string
}

/** CollectiveOfferHistory */
export interface CollectiveOfferHistory {
  future: CollectiveOfferDisplayedStatus[]
  /** Past */
  past: HistoryStep[]
}

/** CollectiveOfferInstitutionModel */
export interface CollectiveOfferInstitutionModel {
  /** City */
  city: string
  /** Institutionid */
  institutionId: string
  /** Institutiontype */
  institutionType: string
  /** Name */
  name: string
  /** Postalcode */
  postalCode: string
}

/** CollectiveOfferLocationModel */
export interface CollectiveOfferLocationModel {
  /** Location */
  location?: LocationBodyModel | LocationOnlyOnVenueBodyModel | null
  /** Locationcomment */
  locationComment?: string | null
  /** An enumeration. */
  locationType: CollectiveLocationType
}

/** CollectiveOfferRedactorModel */
export interface CollectiveOfferRedactorModel {
  /** Email */
  email: string
  /** Firstname */
  firstName?: string | null
  /** Lastname */
  lastName?: string | null
}

/** CollectiveOfferResponseIdModel */
export interface CollectiveOfferResponseIdModel {
  /** Id */
  id: number
}

/** CollectiveOfferResponseModel */
export interface CollectiveOfferResponseModel {
  allowedActions: CollectiveOfferAllowedAction[]
  /** CollectiveOfferDatesModel */
  dates?: CollectiveOfferDatesModel | null
  /** An enumeration. */
  displayedStatus: CollectiveOfferDisplayedStatus
  /** EducationalInstitutionResponseModel */
  educationalInstitution?: EducationalInstitutionResponseModel | null
  /** Id */
  id: number
  /** Imageurl */
  imageUrl?: string | null
  location: GetCollectiveOfferLocationModel
  /** Name */
  name: string
  /** CollectiveOfferStockResponseModel */
  stock?: CollectiveOfferStockResponseModel | null
  venue: ListOffersVenueResponseModel
}

/** CollectiveOfferStockResponseModel */
export interface CollectiveOfferStockResponseModel {
  /**
   * Bookinglimitdatetime
   * @format date-time
   */
  bookingLimitDatetime?: string | null
  /** Numberoftickets */
  numberOfTickets?: number | null
  /** Price */
  price?: number | null
}

/** CollectiveOfferTemplateResponseModel */
export interface CollectiveOfferTemplateResponseModel {
  allowedActions: CollectiveOfferTemplateAllowedAction[]
  /** CollectiveOfferDatesModel */
  dates?: CollectiveOfferDatesModel | null
  /** An enumeration. */
  displayedStatus: CollectiveOfferDisplayedStatus
  /** Id */
  id: number
  /** Imageurl */
  imageUrl?: string | null
  location: GetCollectiveOfferLocationModel
  /** Name */
  name: string
  venue: ListOffersVenueResponseModel
}

/** CollectiveRevenue */
export interface CollectiveRevenue {
  /** Collective */
  collective: number
}

/** CollectiveStockCreationBodyModel */
export interface CollectiveStockCreationBodyModel {
  /** Bookinglimitdatetime */
  bookingLimitDatetime: string | null
  /** Educationalpricedetail */
  educationalPriceDetail: string | null
  /**
   * Enddatetime
   * @format date-time
   */
  endDatetime: string
  /** Numberoftickets */
  numberOfTickets: number
  /** Offerid */
  offerId: number
  /**
   * Startdatetime
   * @format date-time
   */
  startDatetime: string
  /** Totalprice */
  totalPrice: number
}

/** CollectiveStockEditionBodyModel */
export interface CollectiveStockEditionBodyModel {
  /**
   * Bookinglimitdatetime
   * @default null
   */
  bookingLimitDatetime?: string | null
  /**
   * Educationalpricedetail
   * @default null
   */
  educationalPriceDetail?: string | null
  /**
   * Enddatetime
   * @default null
   */
  endDatetime?: string | null
  /**
   * Numberoftickets
   * @default null
   */
  numberOfTickets?: number | null
  /**
   * Startdatetime
   * @default null
   */
  startDatetime?: string | null
  /**
   * Totalprice
   * @default null
   */
  totalPrice?: number | null
}

/** CollectiveStockResponseModel */
export interface CollectiveStockResponseModel {
  /**
   * Bookinglimitdatetime
   * @format date-time
   */
  bookingLimitDatetime: string
  /** Educationalpricedetail */
  educationalPriceDetail: string | null
  /**
   * Enddatetime
   * @format date-time
   */
  endDatetime: string
  /** Id */
  id: number
  /** Numberoftickets */
  numberOfTickets: number
  /** Price */
  price: number
  /**
   * Startdatetime
   * @format date-time
   */
  startDatetime: string
}

/** Consent */
export interface Consent {
  /**
   * Accepted
   * @uniqueItems true
   */
  accepted: string[]
  /**
   * Mandatory
   * @uniqueItems true
   */
  mandatory: string[]
  /**
   * Refused
   * @uniqueItems true
   */
  refused: string[]
}

/** CookieConsentRequest */
export interface CookieConsentRequest {
  /**
   * Choicedatetime
   * @format date-time
   */
  choiceDatetime: string
  consent: Consent
  /** Deviceid */
  deviceId: string
  /** Userid */
  userId?: number | null
}

/** CreateOfferHighlightRequestBodyModel */
export interface CreateOfferHighlightRequestBodyModel {
  /** Highlight Ids */
  highlight_ids: number[]
}

/** CreateOffererQueryModel */
export interface CreateOffererQueryModel {
  /** City */
  city: string
  /** Inseecode */
  inseeCode?: string | null
  /** Latitude */
  latitude?: number | null
  /** Longitude */
  longitude?: number | null
  /** Name */
  name: string
  /** Phonenumber */
  phoneNumber?: string | null
  /** Postalcode */
  postalCode: string
  /** Siren */
  siren: string
  /** Street */
  street?: string | null
}

/** CreatePriceCategoryModel */
export interface CreatePriceCategoryModel {
  /**
   * Label
   * @minLength 1
   * @maxLength 50
   */
  label: string
  /** Price */
  price: number
}

/** CreateThumbnailBodyModel */
export interface CreateThumbnailBodyModel {
  /**
   * Credit
   * @default null
   */
  credit?: string | null
  /**
   * Croppingrectheight
   * @default null
   */
  croppingRectHeight?: number | null
  /**
   * Croppingrectwidth
   * @default null
   */
  croppingRectWidth?: number | null
  /**
   * Croppingrectx
   * @default null
   */
  croppingRectX?: number | null
  /**
   * Croppingrecty
   * @default null
   */
  croppingRectY?: number | null
  /** Offerid */
  offerId: number
}

/** CreateThumbnailResponseModel */
export interface CreateThumbnailResponseModel {
  /**
   * Credit
   * @default null
   */
  credit?: string | null
  /** Id */
  id: number
  /** Url */
  url: string
}

/** CropParams */
export interface CropParams {
  /**
   * Height Crop Percent
   * @min 0
   * @max 1
   * @default 1
   */
  height_crop_percent?: number
  /**
   * Width Crop Percent
   * @min 0
   * @max 1
   * @default 1
   */
  width_crop_percent?: number
  /**
   * X Crop Percent
   * @min 0
   * @max 1
   * @default 0
   */
  x_crop_percent?: number
  /**
   * Y Crop Percent
   * @min 0
   * @max 1
   * @default 0
   */
  y_crop_percent?: number
}

/** DMSApplicationForEAC */
export interface DMSApplicationForEAC {
  /** Application */
  application: number
  /**
   * Builddate
   * @format date-time
   */
  buildDate?: string | null
  /**
   * Depositdate
   * @format date-time
   */
  depositDate: string
  /**
   * Expirationdate
   * @format date-time
   */
  expirationDate?: string | null
  /**
   * Instructiondate
   * @format date-time
   */
  instructionDate?: string | null
  /**
   * Lastchangedate
   * @format date-time
   */
  lastChangeDate: string
  /** Procedure */
  procedure: number
  /**
   * Processingdate
   * @format date-time
   */
  processingDate?: string | null
  /** An enumeration. */
  state: DMSApplicationstatus
  /**
   * Userdeletiondate
   * @format date-time
   */
  userDeletionDate?: string | null
  /** Venueid */
  venueId: number
}

/** DateRangeModel */
export interface DateRangeModel {
  /**
   * End
   * @format date-time
   */
  end: string
  /**
   * Start
   * @format date-time
   */
  start: string
}

/** DateRangeOnCreateModel */
export interface DateRangeOnCreateModel {
  /**
   * End
   * @format date-time
   */
  end: string
  /**
   * Start
   * @format date-time
   */
  start: string
}

/** DeleteOfferRequestBody */
export interface DeleteOfferRequestBody {
  /** Ids */
  ids: number[]
}

/** DeleteStockListBody */
export interface DeleteStockListBody {
  /**
   * Ids To Delete
   * @maxItems 50
   */
  ids_to_delete: number[]
}

/** EditPriceCategoryModel */
export interface EditPriceCategoryModel {
  /** Id */
  id: number
  /**
   * Label
   * @minLength 1
   * @maxLength 50
   */
  label: string
  /** Price */
  price: number
}

/** EditVenueBodyModel */
export interface EditVenueBodyModel {
  /** Activity */
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /**
   * Banid
   * @maxLength 50
   */
  banId?: string | null
  /**
   * Bookingemail
   * @format email
   */
  bookingEmail?: string | null
  /**
   * City
   * @minLength 1
   * @maxLength 200
   */
  city?: string | null
  /**
   * Comment
   * @maxLength 500
   */
  comment?: string | null
  /** VenueContactModel */
  contact?: VenueContactModel | null
  /** Culturaldomains */
  culturalDomains?: string[] | null
  /**
   * Description
   * @maxLength 1000
   */
  description?: string | null
  /** Inseecode */
  inseeCode?: string | null
  /** Isaccessibilityappliedonalloffers */
  isAccessibilityAppliedOnAllOffers?: boolean | null
  /** Ismanualedition */
  isManualEdition?: boolean | null
  /** Isopentopublic */
  isOpenToPublic?: boolean | null
  /** Latitude */
  latitude?: number | null
  /** Longitude */
  longitude?: number | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /**
   * Name
   * @minLength 1
   * @maxLength 140
   */
  name?: string | null
  /** WeekdayOpeningHoursTimespans */
  openingHours?: WeekdayOpeningHoursTimespans | null
  /**
   * Postalcode
   * @minLength 5
   * @maxLength 5
   */
  postalCode?: string | null
  /**
   * Publicname
   * @maxLength 255
   */
  publicName?: string | null
  /**
   * Siret
   * @minLength 14
   * @maxLength 14
   */
  siret?: string | null
  /**
   * Street
   * @minLength 1
   * @maxLength 200
   */
  street?: string | null
  /** Venuelabelid */
  venueLabelId?: number | null
  venueTypeCode?: VenueTypeCode | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /**
   * Withdrawaldetails
   * @maxLength 500
   */
  withdrawalDetails?: string | null
}

/** EditVenueCollectiveDataBodyModel */
export interface EditVenueCollectiveDataBodyModel {
  /** Collectiveaccessinformation */
  collectiveAccessInformation?: string | null
  /** Collectivedescription */
  collectiveDescription?: string | null
  /** Collectivedomains */
  collectiveDomains?: number[] | null
  /** Collectiveemail */
  collectiveEmail?: string | null
  /** Collectiveinterventionarea */
  collectiveInterventionArea?: string[] | null
  /** Collectivenetwork */
  collectiveNetwork?: string[] | null
  /** Collectivephone */
  collectivePhone?: string | null
  collectiveStudents?: StudentLevels[] | null
  /** Collectivewebsite */
  collectiveWebsite?: string | null
  /** Venueeducationalstatusid */
  venueEducationalStatusId?: number | null
}

/** EducationalDomainResponseModel */
export interface EducationalDomainResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
  /** Nationalprograms */
  nationalPrograms: NationalProgramResponseModel[]
}

/** EducationalDomainsResponseModel */
export type EducationalDomainsResponseModel = EducationalDomainResponseModel[]

/** EducationalInstitutionResponseModel */
export interface EducationalInstitutionResponseModel {
  /** City */
  city: string
  /** Id */
  id: number
  /** Institutionid */
  institutionId: string
  /** Institutiontype */
  institutionType?: string | null
  /** Name */
  name: string
  /** Phonenumber */
  phoneNumber: string
  /** Postalcode */
  postalCode: string
}

/** EducationalInstitutionsQueryModel */
export interface EducationalInstitutionsQueryModel {
  /**
   * Page
   * @default 1
   */
  page?: number
  /**
   * Perpagelimit
   * @default 1000
   */
  perPageLimit?: number
}

/** EducationalInstitutionsResponseModel */
export interface EducationalInstitutionsResponseModel {
  /** Educationalinstitutions */
  educationalInstitutions: EducationalInstitutionResponseModel[]
  /** Page */
  page: number
  /** Pages */
  pages: number
  /** Total */
  total: number
}

/** EducationalRedactor */
export interface EducationalRedactor {
  /** Email */
  email: string
  /** Gender */
  gender?: string | null
  /** Name */
  name: string
  /** Surname */
  surname: string
}

/** EducationalRedactorQueryModel */
export interface EducationalRedactorQueryModel {
  /**
   * Candidate
   * @minLength 3
   */
  candidate: string
  /**
   * Uai
   * @minLength 3
   */
  uai: string
}

/** EducationalRedactorResponseModel */
export interface EducationalRedactorResponseModel {
  /** Civility */
  civility?: string | null
  /** Email */
  email?: string | null
  /** Firstname */
  firstName?: string | null
  /** Lastname */
  lastName?: string | null
}

/** EducationalRedactors */
export type EducationalRedactors = EducationalRedactor[]

/** EventDateScheduleAndPriceCategoriesCountModel */
export interface EventDateScheduleAndPriceCategoriesCountModel {
  /**
   * Eventdate
   * @format date
   */
  eventDate: string
  /** Pricecategoriescount */
  priceCategoriesCount: number
  /** Schedulecount */
  scheduleCount: number
}

/** EventDatesInfos */
export type EventDatesInfos = EventDateScheduleAndPriceCategoriesCountModel[]

/** EventStockCreateBodyModel */
export interface EventStockCreateBodyModel {
  /**
   * Beginningdatetime
   * @format date-time
   */
  beginningDatetime: string
  /**
   * Bookinglimitdatetime
   * @default null
   */
  bookingLimitDatetime?: string | null
  /** Pricecategoryid */
  priceCategoryId: number
  /**
   * Quantity
   * @default null
   */
  quantity?: number | null
}

/** EventStockUpdateBodyModel */
export interface EventStockUpdateBodyModel {
  /**
   * Beginningdatetime
   * @format date-time
   */
  beginningDatetime: string
  /**
   * Bookinglimitdatetime
   * @default null
   */
  bookingLimitDatetime?: string | null
  /** Id */
  id: number
  /** Pricecategoryid */
  priceCategoryId: number
  /**
   * Quantity
   * @default null
   */
  quantity?: number | null
}

/** EventStocksBulkCreateBodyModel */
export interface EventStocksBulkCreateBodyModel {
  /** Offerid */
  offerId: number
  /** Stocks */
  stocks: EventStockCreateBodyModel[]
}

/** EventStocksBulkUpdateBodyModel */
export interface EventStocksBulkUpdateBodyModel {
  /** Offerid */
  offerId: number
  /** Stocks */
  stocks: EventStockUpdateBodyModel[]
}

/** ExternalAccessibilityDataModel */
export interface ExternalAccessibilityDataModel {
  /**
   * Audiodisability
   * @default {"deafAndHardOfHearing":["Non renseigné"]}
   */
  audioDisability?: AudioDisabilityModel
  /**
   * Isaccessibleaudiodisability
   * @default false
   */
  isAccessibleAudioDisability?: boolean
  /**
   * Isaccessiblementaldisability
   * @default false
   */
  isAccessibleMentalDisability?: boolean
  /**
   * Isaccessiblemotordisability
   * @default false
   */
  isAccessibleMotorDisability?: boolean
  /**
   * Isaccessiblevisualdisability
   * @default false
   */
  isAccessibleVisualDisability?: boolean
  /**
   * Mentaldisability
   * @default {"trainedPersonnel":"Non renseigné"}
   */
  mentalDisability?: MentalDisabilityModel
  /**
   * Motordisability
   * @default {"entrance":"Non renseigné","exterior":"Non renseigné","facilities":"Non renseigné","parking":"Non renseigné"}
   */
  motorDisability?: MotorDisabilityModel
  /**
   * Visualdisability
   * @default {"audioDescription":["Non renseigné"],"soundBeacon":"Non renseigné"}
   */
  visualDisability?: VisualDisabilityModel
}

/** FeatureResponseModel */
export interface FeatureResponseModel {
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Name */
  name: string
}

/** FinanceBankAccountListResponseModel */
export type FinanceBankAccountListResponseModel =
  FinanceBankAccountResponseModel[]

/** FinanceBankAccountResponseModel */
export interface FinanceBankAccountResponseModel {
  /** Id */
  id: number
  /** Label */
  label: string
}

/** GetActiveEANOfferResponseModel */
export interface GetActiveEANOfferResponseModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Productid */
  productId?: number | null
  /** An enumeration. */
  status: OfferStatus
  /** An enumeration. */
  subcategoryId: SubcategoryIdEnum
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** GetBookingResponse */
export interface GetBookingResponse {
  /** Bookingid */
  bookingId: string
  /** Dateofbirth */
  dateOfBirth: string | null
  /** Datetime */
  datetime: string
  /** Ean13 */
  ean13: string | null
  /** Email */
  email: string
  /** Firstname */
  firstName: string | null
  /** Isused */
  isUsed: boolean
  /** Lastname */
  lastName: string | null
  /** Offeraddress */
  offerAddress: string | null
  /** Offerdepartmentcode */
  offerDepartmentCode: string | null
  /** Offerid */
  offerId: number
  /** Offername */
  offerName: string
  offerType: BookingOfferType
  /** Phonenumber */
  phoneNumber: string | null
  /** Price */
  price: number
  /** Pricecategorylabel */
  priceCategoryLabel: string | null
  /** Publicofferid */
  publicOfferId: string
  /** Quantity */
  quantity: number
  /** Username */
  userName: string
  /** Venuename */
  venueName: string
}

/** GetCollectiveOfferBookingResponseModel */
export interface GetCollectiveOfferBookingResponseModel {
  /**
   * Cancellationlimitdate
   * @format date-time
   */
  cancellationLimitDate: string
  cancellationReason?: CollectiveBookingCancellationReasons | null
  /**
   * Confirmationlimitdate
   * @format date-time
   */
  confirmationLimitDate: string
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** EducationalRedactorResponseModel */
  educationalRedactor?: EducationalRedactorResponseModel | null
  /** Id */
  id: number
  /** An enumeration. */
  status: CollectiveBookingStatus
}

/** GetCollectiveOfferCollectiveStockResponseModel */
export interface GetCollectiveOfferCollectiveStockResponseModel {
  /**
   * Bookinglimitdatetime
   * @format date-time
   */
  bookingLimitDatetime?: string | null
  /**
   * Educationalpricedetail
   * @maxLength 1000
   */
  educationalPriceDetail?: string | null
  /**
   * Enddatetime
   * @format date-time
   */
  endDatetime?: string | null
  /** Id */
  id: number
  /** Isbooked */
  isBooked: boolean
  /** Numberoftickets */
  numberOfTickets?: number | null
  /** Price */
  price: number
  /**
   * Startdatetime
   * @format date-time
   */
  startDatetime?: string | null
}

/** GetCollectiveOfferLocationModel */
export interface GetCollectiveOfferLocationModel {
  /** LocationResponseModel */
  location?: LocationResponseModel | null
  /** Locationcomment */
  locationComment?: string | null
  /** An enumeration. */
  locationType: CollectiveLocationType
}

/** GetCollectiveOfferManagingOffererResponseModel */
export interface GetCollectiveOfferManagingOffererResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Id */
  id: number
  /** Name */
  name: string
  /** Siren */
  siren: string
}

/** GetCollectiveOfferProviderResponseModel */
export interface GetCollectiveOfferProviderResponseModel {
  /** Name */
  name: string
}

/** GetCollectiveOfferRequestResponseModel */
export interface GetCollectiveOfferRequestResponseModel {
  /** Comment */
  comment: string
  /**
   * Datecreated
   * @format date
   */
  dateCreated?: string | null
  institution: CollectiveOfferInstitutionModel
  /** Phonenumber */
  phoneNumber?: string | null
  redactor: CollectiveOfferRedactorModel
  /**
   * Requesteddate
   * @format date
   */
  requestedDate?: string | null
  /** Totalstudents */
  totalStudents?: number | null
  /** Totalteachers */
  totalTeachers?: number | null
}

/** GetCollectiveOfferResponseModel */
export interface GetCollectiveOfferResponseModel {
  allowedActions: CollectiveOfferAllowedAction[]
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** GetCollectiveOfferBookingResponseModel */
  booking?: GetCollectiveOfferBookingResponseModel | null
  /** Bookingemails */
  bookingEmails: string[]
  /** GetCollectiveOfferCollectiveStockResponseModel */
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel | null
  /** Contactemail */
  contactEmail?: string | null
  /** Contactphone */
  contactPhone?: string | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** CollectiveOfferDatesModel */
  dates?: CollectiveOfferDatesModel | null
  /** Description */
  description: string
  /** An enumeration. */
  displayedStatus: CollectiveOfferDisplayedStatus
  /** Domains */
  domains: OfferDomain[]
  /** Durationminutes */
  durationMinutes?: number | null
  formats: EacFormat[]
  /** Hasbookinglimitdatetimespassed */
  hasBookingLimitDatetimesPassed: boolean
  history: CollectiveOfferHistory
  /** Id */
  id: number
  /** Imagecredit */
  imageCredit?: string | null
  /** Imageurl */
  imageUrl?: string | null
  /** EducationalInstitutionResponseModel */
  institution?: EducationalInstitutionResponseModel | null
  /** Interventionarea */
  interventionArea: string[]
  /** Isactive */
  isActive: boolean
  /** Isbookable */
  isBookable: boolean
  /** Isnonfreeoffer */
  isNonFreeOffer?: boolean | null
  /** Ispublicapi */
  isPublicApi: boolean
  /**
   * Istemplate
   * @default false
   */
  isTemplate?: boolean
  location: GetCollectiveOfferLocationModel
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** NationalProgramModel */
  nationalProgram?: NationalProgramModel | null
  /** GetCollectiveOfferProviderResponseModel */
  provider?: GetCollectiveOfferProviderResponseModel | null
  students: StudentLevels[]
  /** EducationalRedactorResponseModel */
  teacher?: EducationalRedactorResponseModel | null
  /** Templateid */
  templateId?: number | null
  venue: GetCollectiveOfferVenueResponseModel
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** GetCollectiveOfferTemplateResponseModel */
export interface GetCollectiveOfferTemplateResponseModel {
  allowedActions: CollectiveOfferTemplateAllowedAction[]
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** Bookingemails */
  bookingEmails: string[]
  /** Contactemail */
  contactEmail?: string | null
  contactForm?: OfferContactFormEnum | null
  /** Contactphone */
  contactPhone?: string | null
  /** Contacturl */
  contactUrl?: string | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** CollectiveOfferDatesModel */
  dates?: CollectiveOfferDatesModel | null
  /** Description */
  description: string
  /** An enumeration. */
  displayedStatus: CollectiveOfferDisplayedStatus
  /** Domains */
  domains: OfferDomain[]
  /** Durationminutes */
  durationMinutes?: number | null
  /**
   * Educationalpricedetail
   * @maxLength 1000
   */
  educationalPriceDetail?: string | null
  formats: EacFormat[]
  /** Hasbookinglimitdatetimespassed */
  hasBookingLimitDatetimesPassed: boolean
  /** Id */
  id: number
  /** Imagecredit */
  imageCredit?: string | null
  /** Imageurl */
  imageUrl?: string | null
  /** Interventionarea */
  interventionArea: string[]
  /** Isactive */
  isActive: boolean
  /** Isnonfreeoffer */
  isNonFreeOffer?: boolean | null
  /**
   * Istemplate
   * @default true
   */
  isTemplate?: boolean
  location: GetCollectiveOfferLocationModel
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** NationalProgramModel */
  nationalProgram?: NationalProgramModel | null
  students: StudentLevels[]
  venue: GetCollectiveOfferVenueResponseModel
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** GetCollectiveOfferVenueResponseModel */
export interface GetCollectiveOfferVenueResponseModel {
  /** Departementcode */
  departementCode?: string | null
  /** Id */
  id: number
  /** Imgurl */
  imgUrl?: string | null
  managingOfferer: GetCollectiveOfferManagingOffererResponseModel
  /** Name */
  name: string
  /** Publicname */
  publicName?: string | null
}

/** GetCombinedInvoicesQueryModel */
export interface GetCombinedInvoicesQueryModel {
  /** Invoicereferences */
  invoiceReferences: string[]
}

/** GetEducationalOffererResponseModel */
export interface GetEducationalOffererResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Id */
  id: number
  /** Managedvenues */
  managedVenues: GetEducationalOffererVenueResponseModel[]
  /** Name */
  name: string
}

/** GetEducationalOffererVenueResponseModel */
export interface GetEducationalOffererVenueResponseModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** City */
  city?: string | null
  /** Collectiveemail */
  collectiveEmail?: string | null
  /** Collectiveinterventionarea */
  collectiveInterventionArea?: string[] | null
  /** Collectivephone */
  collectivePhone?: string | null
  /** Id */
  id: number
  /** Isvirtual */
  isVirtual: boolean
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Postalcode */
  postalCode?: string | null
  /** Publicname */
  publicName?: string | null
  /** Street */
  street?: string | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** GetEducationalOfferersQueryModel */
export interface GetEducationalOfferersQueryModel {
  /** Offerer Id */
  offerer_id?: number | null
}

/** GetEducationalOfferersResponseModel */
export interface GetEducationalOfferersResponseModel {
  /** Educationalofferers */
  educationalOfferers: GetEducationalOffererResponseModel[]
}

/** GetIndividualOfferResponseModel */
export interface GetIndividualOfferResponseModel {
  /** GetOfferMediationResponseModel */
  activeMediation?: GetOfferMediationResponseModel | null
  /** Artistofferlinks */
  artistOfferLinks: ArtistOfferResponseModel[]
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /**
   * Bookingalloweddatetime
   * @format date-time
   */
  bookingAllowedDatetime?: string | null
  /** Bookingcontact */
  bookingContact?: string | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** Bookingscount */
  bookingsCount?: number | null
  /** Canbeevent */
  canBeEvent: boolean
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** Description */
  description?: string | null
  /** Durationminutes */
  durationMinutes?: number | null
  /** Externalticketofficeurl */
  externalTicketOfficeUrl?: string | null
  /** Extradata */
  extraData?: any
  /** Hasbookinglimitdatetimespassed */
  hasBookingLimitDatetimesPassed: boolean
  /** Hasstocks */
  hasStocks: boolean
  /** Highlightrequests */
  highlightRequests: ShortHighlightResponseModel[]
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Isdigital */
  isDigital: boolean
  /** Isduo */
  isDuo: boolean
  /** Iseditable */
  isEditable: boolean
  /** Isevent */
  isEvent: boolean
  /** Isnational */
  isNational: boolean
  /** Isnonfreeoffer */
  isNonFreeOffer?: boolean | null
  /** Isthing */
  isThing: boolean
  /** GetOfferLastProviderResponseModel */
  lastProvider?: GetOfferLastProviderResponseModel | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Pricecategories */
  priceCategories?: PriceCategoryResponseModel[] | null
  /** Productid */
  productId?: number | null
  /**
   * Publicationdate
   * @format date-time
   */
  publicationDate?: string | null
  /**
   * Publicationdatetime
   * @format date-time
   */
  publicationDatetime?: string | null
  /** An enumeration. */
  status: OfferStatus
  /** An enumeration. */
  subcategoryId: SubcategoryIdEnum
  /** Thumburl */
  thumbUrl?: string | null
  /** Url */
  url?: string | null
  venue: GetOfferVenueResponseModel
  videoData: VideoData
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /** Withdrawaldelay */
  withdrawalDelay?: number | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
  withdrawalType?: WithdrawalTypeEnum | null
}

/** GetIndividualOfferWithAddressResponseModel */
export interface GetIndividualOfferWithAddressResponseModel {
  /** GetOfferMediationResponseModel */
  activeMediation?: GetOfferMediationResponseModel | null
  /** Artistofferlinks */
  artistOfferLinks: ArtistOfferResponseModel[]
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /**
   * Bookingalloweddatetime
   * @format date-time
   */
  bookingAllowedDatetime?: string | null
  /** Bookingcontact */
  bookingContact?: string | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** Bookingscount */
  bookingsCount?: number | null
  /** Canbeevent */
  canBeEvent: boolean
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** Description */
  description?: string | null
  /** Durationminutes */
  durationMinutes?: number | null
  /** Externalticketofficeurl */
  externalTicketOfficeUrl?: string | null
  /** Extradata */
  extraData?: any
  /** Hasbookinglimitdatetimespassed */
  hasBookingLimitDatetimesPassed: boolean
  /** Haspendingbookings */
  hasPendingBookings: boolean
  /** Hasstocks */
  hasStocks: boolean
  /** Highlightrequests */
  highlightRequests: ShortHighlightResponseModel[]
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Isdigital */
  isDigital: boolean
  /** Isduo */
  isDuo: boolean
  /** Iseditable */
  isEditable: boolean
  /** Isevent */
  isEvent: boolean
  /** Isheadlineoffer */
  isHeadlineOffer: boolean
  /** Isnational */
  isNational: boolean
  /** Isnonfreeoffer */
  isNonFreeOffer?: boolean | null
  /** Isthing */
  isThing: boolean
  /** GetOfferLastProviderResponseModel */
  lastProvider?: GetOfferLastProviderResponseModel | null
  /** LocationResponseModel */
  location?: LocationResponseModel | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Pricecategories */
  priceCategories?: PriceCategoryResponseModel[] | null
  /** Productid */
  productId?: number | null
  /**
   * Publicationdate
   * @format date-time
   */
  publicationDate?: string | null
  /**
   * Publicationdatetime
   * @format date-time
   */
  publicationDatetime?: string | null
  /** An enumeration. */
  status: OfferStatus
  /** An enumeration. */
  subcategoryId: SubcategoryIdEnum
  /** Thumburl */
  thumbUrl?: string | null
  /** Url */
  url?: string | null
  venue: GetOfferVenueResponseModel
  videoData: VideoData
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /** Withdrawaldelay */
  withdrawalDelay?: number | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
  withdrawalType?: WithdrawalTypeEnum | null
}

/** GetMusicTypesResponse */
export type GetMusicTypesResponse = MusicTypeResponse[]

/** GetOfferLastProviderResponseModel */
export interface GetOfferLastProviderResponseModel {
  /** Name */
  name: string
}

/** GetOfferManagingOffererResponseModel */
export interface GetOfferManagingOffererResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Id */
  id: number
  /** Name */
  name: string
}

/** GetOfferMediationResponseModel */
export interface GetOfferMediationResponseModel {
  /** Authorid */
  authorId?: string | null
  /** Credit */
  credit?: string | null
  /** Thumburl */
  thumbUrl?: string | null
}

/** GetOfferStockResponseModel */
export interface GetOfferStockResponseModel {
  /**
   * Activationcodesexpirationdatetime
   * @format date-time
   */
  activationCodesExpirationDatetime?: string | null
  /**
   * Beginningdatetime
   * @format date-time
   */
  beginningDatetime?: string | null
  /**
   * Bookinglimitdatetime
   * @format date-time
   */
  bookingLimitDatetime?: string | null
  /** Bookingsquantity */
  bookingsQuantity: number
  /** Hasactivationcode */
  hasActivationCode: boolean
  /** Id */
  id: number
  /** Iseventdeletable */
  isEventDeletable: boolean
  /** Price */
  price: number
  /** Pricecategoryid */
  priceCategoryId?: number | null
  /** Quantity */
  quantity?: number | null
  /** Remainingquantity */
  remainingQuantity?: number | string | null
}

/** GetOfferVenueResponseModel */
export interface GetOfferVenueResponseModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** City */
  city?: string | null
  /** Departementcode */
  departementCode?: string | null
  /** Id */
  id: number
  /** Isvirtual */
  isVirtual: boolean
  managingOfferer: GetOfferManagingOffererResponseModel
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Postalcode */
  postalCode?: string | null
  /** Publicname */
  publicName?: string | null
  /** Street */
  street?: string | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** GetOffererAddressResponseModel */
export interface GetOffererAddressResponseModel {
  /** City */
  city: string
  /** Departmentcode */
  departmentCode?: string | null
  /** Id */
  id: number
  /** Islinkedtovenue */
  isLinkedToVenue: boolean
  /** Label */
  label?: string | null
  /** Postalcode */
  postalCode: string
  /** Street */
  street?: string | null
}

/** GetOffererAddressesQueryModel */
export interface GetOffererAddressesQueryModel {
  withOffersOption?: GetOffererAddressesWithOffersOption | null
}

/** GetOffererAddressesResponseModel */
export type GetOffererAddressesResponseModel = GetOffererAddressResponseModel[]

/** GetOffererBankAccountsResponseModel */
export interface GetOffererBankAccountsResponseModel {
  /** Bankaccounts */
  bankAccounts: BankAccountResponseModel[]
  /** Id */
  id: number
  /** Managedvenues */
  managedVenues: ManagedVenue[]
}

/** GetOffererMemberResponseModel */
export interface GetOffererMemberResponseModel {
  /** Email */
  email: string
  /** An enumeration. */
  status: OffererMemberStatus
}

/** GetOffererMembersResponseModel */
export interface GetOffererMembersResponseModel {
  /** Members */
  members: GetOffererMemberResponseModel[]
}

/** GetOffererNameResponseModel */
export interface GetOffererNameResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Id */
  id: number
  /** Name */
  name: string
}

/** GetOffererResponseModel */
export interface GetOffererResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Candisplayhighlights */
  canDisplayHighlights: boolean
  /** Hasactiveoffer */
  hasActiveOffer: boolean
  /** Hasavailablepricingpoints */
  hasAvailablePricingPoints: boolean
  /** Hasbankaccountwithpendingcorrections */
  hasBankAccountWithPendingCorrections: boolean
  /** Hasdigitalvenueatleastoneoffer */
  hasDigitalVenueAtLeastOneOffer: boolean
  /** Hasheadlineoffer */
  hasHeadlineOffer: boolean
  /** Hasnonfreeoffer */
  hasNonFreeOffer: boolean
  /** Haspartnerpage */
  hasPartnerPage: boolean
  /** Haspendingbankaccount */
  hasPendingBankAccount: boolean
  /** Hasvalidbankaccount */
  hasValidBankAccount: boolean
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Iscaledonian */
  isCaledonian: boolean
  /** Isonboarded */
  isOnboarded: boolean
  /** Isvalidated */
  isValidated: boolean
  /**
   * Managedvenues
   * @default []
   */
  managedVenues?: GetOffererVenueResponseModel[]
  /** Name */
  name: string
  /** Siren */
  siren: string
  /** Venueswithnonfreeofferswithoutbankaccounts */
  venuesWithNonFreeOffersWithoutBankAccounts: number[]
}

/** GetOffererStatsResponseModel */
export interface GetOffererStatsResponseModel {
  jsonData: OffererStatsDataModel
  /** Offererid */
  offererId: number
  /**
   * Syncdate
   * @format date-time
   */
  syncDate?: string | null
}

/** GetOffererV2StatsResponseModel */
export interface GetOffererV2StatsResponseModel {
  /** Pendingeducationaloffers */
  pendingEducationalOffers: number
  /** Pendingpublicoffers */
  pendingPublicOffers: number
  /** Publishededucationaloffers */
  publishedEducationalOffers: number
  /** Publishedpublicoffers */
  publishedPublicOffers: number
}

/** GetOffererVenueResponseModel */
export interface GetOffererVenueResponseModel {
  activity?: DisplayableActivity | null
  /** BannerMetaModel */
  bannerMeta?: BannerMetaModel | null
  /** Bannerurl */
  bannerUrl?: string | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** Collectivedmsapplications */
  collectiveDmsApplications: DMSApplicationForEAC[]
  /** Hasadageid */
  hasAdageId: boolean
  /** Hascreatedoffer */
  hasCreatedOffer: boolean
  /** Haspartnerpage */
  hasPartnerPage: boolean
  /** Hasvenueproviders */
  hasVenueProviders: boolean
  /** Id */
  id: number
  /** Ispermanent */
  isPermanent: boolean
  /** Isvirtual */
  isVirtual: boolean
  /** Name */
  name: string
  /** Publicname */
  publicName?: string | null
  /** Siret */
  siret?: string | null
  venueTypeCode?: VenueTypeCode | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
}

/** GetOfferersNamesQueryModel */
export interface GetOfferersNamesQueryModel {
  /** Offerer Id */
  offerer_id?: number | null
  /** Validated */
  validated?: boolean | null
  /** Validated For User */
  validated_for_user?: boolean | null
}

/** GetOfferersNamesResponseModel */
export interface GetOfferersNamesResponseModel {
  /** Offerersnames */
  offerersNames: GetOffererNameResponseModel[]
}

/** GetOffersStatsResponseModel */
export interface GetOffersStatsResponseModel {
  /** Pendingeducationaloffers */
  pendingEducationalOffers: number
  /** Pendingpublicoffers */
  pendingPublicOffers: number
  /** Publishededucationaloffers */
  publishedEducationalOffers: number
  /** Publishedpublicoffers */
  publishedPublicOffers: number
}

/** GetProductInformations */
export interface GetProductInformations {
  /** Author */
  author: string
  /** Description */
  description?: string | null
  /** Gtlid */
  gtlId: string
  /** Id */
  id: number
  /** Images */
  images: object
  /** Name */
  name: string
  /** Performer */
  performer: string
  /** Subcategoryid */
  subcategoryId: string
}

/** GetStocksResponseModel */
export interface GetStocksResponseModel {
  /** Editedstockcount */
  editedStockCount: number
  /** Stocks */
  stocks: GetOfferStockResponseModel[]
  /** Totalstockcount */
  totalStockCount: number
}

/** GetVenueDomainResponseModel */
export interface GetVenueDomainResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** GetVenueListLiteResponseModel */
export interface GetVenueListLiteResponseModel {
  /** Venues */
  venues: VenueListItemLiteResponseModel[]
}

/** GetVenueListResponseModel */
export interface GetVenueListResponseModel {
  /** Venues */
  venues: VenueListItemResponseModel[]
}

/** GetVenueManagingOffererResponseModel */
export interface GetVenueManagingOffererResponseModel {
  /** Allowedonadage */
  allowedOnAdage: boolean
  /** Id */
  id: number
  /** Isvalidated */
  isValidated: boolean
  /** Name */
  name: string
  /** Siren */
  siren: string
}

/** GetVenuePricingPointResponseModel */
export interface GetVenuePricingPointResponseModel {
  /** Id */
  id: number
  /** Siret */
  siret: string
  /** Venuename */
  venueName: string
}

/** GetVenueResponseModel */
export interface GetVenueResponseModel {
  activity?: DisplayableActivity | null
  /**
   * Adageinscriptiondate
   * @format date-time
   */
  adageInscriptionDate?: string | null
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  bankAccountStatus?: SimplifiedBankAccountStatus | null
  /** BannerMetaModel */
  bannerMeta?: BannerMetaModel | null
  /** Bannerurl */
  bannerUrl?: string | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** Collectiveaccessinformation */
  collectiveAccessInformation?: string | null
  /** Collectivedescription */
  collectiveDescription?: string | null
  /** Collectivedmsapplications */
  collectiveDmsApplications: DMSApplicationForEAC[]
  /** Collectivedomains */
  collectiveDomains: GetVenueDomainResponseModel[]
  /** Collectiveemail */
  collectiveEmail?: string | null
  /** Collectiveinterventionarea */
  collectiveInterventionArea?: string[] | null
  /** LegalStatusResponseModel */
  collectiveLegalStatus?: LegalStatusResponseModel | null
  /** Collectivenetwork */
  collectiveNetwork?: string[] | null
  /** Collectivephone */
  collectivePhone?: string | null
  collectiveStudents?: StudentLevels[] | null
  /** Collectivewebsite */
  collectiveWebsite?: string | null
  /** Comment */
  comment?: string | null
  /** VenueContactModel */
  contact?: VenueContactModel | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /**
   * Description
   * @maxLength 1000
   */
  description?: string | null
  /** Dmstoken */
  dmsToken: string
  /** ExternalAccessibilityDataModel */
  externalAccessibilityData?: ExternalAccessibilityDataModel | null
  /** Externalaccessibilityid */
  externalAccessibilityId?: string | null
  /** Externalaccessibilityurl */
  externalAccessibilityUrl?: string | null
  /** Hasactiveindividualoffer */
  hasActiveIndividualOffer: boolean
  /** Hasadageid */
  hasAdageId: boolean
  /** Hasnonfreeoffers */
  hasNonFreeOffers: boolean
  /** Hasoffers */
  hasOffers: boolean
  /** Haspartnerpage */
  hasPartnerPage: boolean
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Iscaledonian */
  isCaledonian: boolean
  /** Isopentopublic */
  isOpenToPublic: boolean
  /** Ispermanent */
  isPermanent?: boolean | null
  /** Isvalidated */
  isValidated: boolean
  /** Isvirtual */
  isVirtual: boolean
  /** LocationResponseModel */
  location?: LocationResponseModel | null
  managingOfferer: GetVenueManagingOffererResponseModel
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** WeekdayOpeningHoursTimespans */
  openingHours?: WeekdayOpeningHoursTimespans | null
  /** GetVenuePricingPointResponseModel */
  pricingPoint?: GetVenuePricingPointResponseModel | null
  /** Publicname */
  publicName?: string | null
  /** Siret */
  siret?: string | null
  /** Venuelabelid */
  venueLabelId?: number | null
  venueType: VenueTypeResponseModel
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
}

/** GetVenuesOfOffererFromSiretResponseModel */
export interface GetVenuesOfOffererFromSiretResponseModel {
  /** Offerername */
  offererName?: string | null
  /** Offerersiren */
  offererSiren?: string | null
  /** Venues */
  venues: VenueOfOffererFromSiretResponseModel[]
}

/** HasInvoiceQueryModel */
export interface HasInvoiceQueryModel {
  /** Offererid */
  offererId: number
}

/** HasInvoiceResponseModel */
export interface HasInvoiceResponseModel {
  /** Hasinvoice */
  hasInvoice: boolean
}

/** HeadLineOfferResponseModel */
export interface HeadLineOfferResponseModel {
  /** Id */
  id: number
  /** @default null */
  image?: OfferImageV2 | null
  /** Name */
  name: string
  /** Venueid */
  venueId: number
}

/** HeadlineOfferCreationBodyModel */
export interface HeadlineOfferCreationBodyModel {
  /** Offerid */
  offerId: number
}

/** HeadlineOfferDeleteBodyModel */
export interface HeadlineOfferDeleteBodyModel {
  /** Offererid */
  offererId: number
}

/** HighlightResponseModel */
export interface HighlightResponseModel {
  /** Availabilitydatespan */
  availabilityDatespan: string[]
  /**
   * Communicationdate
   * @format date
   */
  communicationDate: string
  /** Description */
  description: string
  /** Highlightdatespan */
  highlightDatespan: string[]
  /** Id */
  id: number
  /** Mediationurl */
  mediationUrl: string
  /** Name */
  name: string
}

/** HighlightsResponseModel */
export type HighlightsResponseModel = HighlightResponseModel[]

/** HistoryStep */
export interface HistoryStep {
  /**
   * Datetime
   * @format date-time
   */
  datetime?: string | null
  /** An enumeration. */
  status: CollectiveOfferDisplayedStatus
}

/** IndividualRevenue */
export interface IndividualRevenue {
  /** Individual */
  individual: number
}

/** InviteMemberQueryModel */
export interface InviteMemberQueryModel {
  /** Email */
  email: string
}

/** InvoiceListV2QueryModel */
export interface InvoiceListV2QueryModel {
  /**
   * Bankaccountid
   * @default null
   */
  bankAccountId?: number | null
  /**
   * Offererid
   * @default null
   */
  offererId?: number | null
  /**
   * Periodbeginningdate
   * @default null
   */
  periodBeginningDate?: string | null
  /**
   * Periodendingdate
   * @default null
   */
  periodEndingDate?: string | null
}

/** InvoiceListV2ResponseModel */
export type InvoiceListV2ResponseModel = InvoiceResponseV2Model[]

/** InvoiceResponseV2Model */
export interface InvoiceResponseV2Model {
  /** Amount */
  amount: number
  /** Bankaccountlabel */
  bankAccountLabel: string | null
  /** Cashflowlabels */
  cashflowLabels: string[]
  /**
   * Date
   * @format date
   */
  date: string
  /** Reference */
  reference: string
  /** Url */
  url: string
}

/** LegalStatusResponseModel */
export interface LegalStatusResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** LinkVenueToBankAccountBodyModel */
export interface LinkVenueToBankAccountBodyModel {
  /**
   * Venues Ids
   * @uniqueItems true
   */
  venues_ids: number[]
}

/** LinkVenueToPricingPointBodyModel */
export interface LinkVenueToPricingPointBodyModel {
  /** Pricingpointid */
  pricingPointId: number
}

/**
 * LinkedVenue
 * A venue that is already linked to a bank account.
 */
export interface LinkedVenue {
  /** Commonname */
  commonName: string
  /** Id */
  id: number
}

/** ListBookingsQueryModel */
export interface ListBookingsQueryModel {
  /**
   * Bookingperiodbeginningdate
   * @default null
   */
  bookingPeriodBeginningDate?: string | null
  /**
   * Bookingperiodendingdate
   * @default null
   */
  bookingPeriodEndingDate?: string | null
  /** @default null */
  bookingStatusFilter?: BookingStatusFilter | null
  /**
   * Eventdate
   * @default null
   */
  eventDate?: string | null
  /** @default null */
  exportType?: BookingExportType | null
  /**
   * Offerid
   * @default null
   */
  offerId?: number | null
  /**
   * Offereraddressid
   * @default null
   */
  offererAddressId?: number | null
  /**
   * Offererid
   * @default null
   */
  offererId?: number | null
  /**
   * Page
   * @default 1
   */
  page?: number
  /**
   * Venueid
   * @default null
   */
  venueId?: number | null
}

/** ListBookingsResponseModel */
export interface ListBookingsResponseModel {
  /** Bookingsrecap */
  bookingsRecap: BookingRecapResponseModel[]
  /** Page */
  page: number
  /** Pages */
  pages: number
  /** Total */
  total: number
}

/** ListCollectiveOfferTemplatesResponseModel */
export type ListCollectiveOfferTemplatesResponseModel =
  CollectiveOfferTemplateResponseModel[]

/** ListCollectiveOffersQueryModel */
export interface ListCollectiveOffersQueryModel {
  format?: EacFormat | null
  locationType?: CollectiveLocationType | null
  /** Name */
  name?: string | null
  /** Offereraddressid */
  offererAddressId?: number | null
  /** Offererid */
  offererId?: number | null
  /**
   * Periodbeginningdate
   * @format date
   */
  periodBeginningDate?: string | null
  /**
   * Periodendingdate
   * @format date
   */
  periodEndingDate?: string | null
  status?: CollectiveOfferDisplayedStatus[] | null
  /** Venueid */
  venueId?: number | null
}

/** ListCollectiveOffersResponseModel */
export type ListCollectiveOffersResponseModel = CollectiveOfferResponseModel[]

/** ListFeatureResponseModel */
export type ListFeatureResponseModel = FeatureResponseModel[]

/** ListOffersOfferResponseModel */
export interface ListOffersOfferResponseModel {
  /**
   * Bookingalloweddatetime
   * @format date-time
   */
  bookingAllowedDatetime?: string | null
  /** Bookingscount */
  bookingsCount?: number | null
  /** Canbeevent */
  canBeEvent: boolean
  /** Hasbookinglimitdatetimespassed */
  hasBookingLimitDatetimesPassed: boolean
  /** Highlightrequests */
  highlightRequests: ShortHighlightResponseModel[]
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Isdigital */
  isDigital: boolean
  /** Iseditable */
  isEditable: boolean
  /** Iseducational */
  isEducational: boolean
  /** Isevent */
  isEvent: boolean
  /** Isheadlineoffer */
  isHeadlineOffer: boolean
  /** Isshowcase */
  isShowcase?: boolean | null
  /** Isthing */
  isThing: boolean
  /** LocationResponseModel */
  location?: LocationResponseModel | null
  /** Name */
  name: string
  /** Productid */
  productId?: number | null
  /** Productisbn */
  productIsbn?: string | null
  /**
   * Publicationdatetime
   * @format date-time
   */
  publicationDatetime?: string | null
  /** An enumeration. */
  status: OfferStatus
  /** Stocks */
  stocks: ListOffersStockResponseModel[]
  /** An enumeration. */
  subcategoryId: SubcategoryIdEnum
  /** Thumburl */
  thumbUrl?: string | null
  venue: ListOffersVenueResponseModel
}

/** ListOffersQueryModel */
export interface ListOffersQueryModel {
  /** Categoryid */
  categoryId?: string | null
  /** Creationmode */
  creationMode?: string | null
  /** Nameorisbn */
  nameOrIsbn?: string | null
  /** Offereraddressid */
  offererAddressId?: number | null
  /** Offererid */
  offererId?: number | null
  /**
   * Periodbeginningdate
   * @format date
   */
  periodBeginningDate?: string | null
  /**
   * Periodendingdate
   * @format date
   */
  periodEndingDate?: string | null
  /** Status */
  status?: OfferStatus | CollectiveOfferDisplayedStatus | null
  /** Venueid */
  venueId?: number | null
}

/** ListOffersResponseModel */
export type ListOffersResponseModel = ListOffersOfferResponseModel[]

/** ListOffersStockResponseModel */
export interface ListOffersStockResponseModel {
  /**
   * Beginningdatetime
   * @format date-time
   */
  beginningDatetime?: string | null
  /** Bookingquantity */
  bookingQuantity?: number | null
  /** Hasbookinglimitdatetimepassed */
  hasBookingLimitDatetimePassed: boolean
  /** Id */
  id: number
  /** Remainingquantity */
  remainingQuantity: number | string
}

/** ListOffersVenueResponseModel */
export interface ListOffersVenueResponseModel {
  /** Departementcode */
  departementCode?: string | null
  /** Id */
  id: number
  /** Isvirtual */
  isVirtual: boolean
  /** Name */
  name: string
  /** Offerername */
  offererName: string
  /** Publicname */
  publicName?: string | null
}

/** ListProviderResponse */
export type ListProviderResponse = ProviderResponse[]

/** ListVenueProviderQuery */
export interface ListVenueProviderQuery {
  /** Venueid */
  venueId: number
}

/** ListVenueProviderResponse */
export interface ListVenueProviderResponse {
  /** Venueproviders */
  venueProviders: VenueProviderResponse[]
}

/** LocationBodyModel */
export interface LocationBodyModel {
  /** Banid */
  banId?: string | null
  /**
   * City
   * @minLength 1
   * @maxLength 200
   */
  city: string
  /**
   * Inseecode
   * @minLength 5
   * @maxLength 5
   */
  inseeCode?: string | null
  /**
   * Ismanualedition
   * @default false
   */
  isManualEdition?: boolean
  /**
   * Isvenuelocation
   * @default false
   */
  isVenueLocation?: boolean
  /** Label */
  label?: string | null
  /** Latitude */
  latitude: number | string
  /** Longitude */
  longitude: number | string
  /**
   * Postalcode
   * @minLength 5
   * @maxLength 5
   */
  postalCode: string
  /**
   * Street
   * @minLength 1
   * @maxLength 200
   */
  street: string
}

/** LocationModel */
export interface LocationModel {
  /** Banid */
  banId?: string | null
  /**
   * City
   * @minLength 1
   * @maxLength 200
   */
  city: string
  /**
   * Inseecode
   * @minLength 5
   * @maxLength 5
   */
  inseeCode?: string | null
  /**
   * Ismanualedition
   * @default false
   */
  isManualEdition?: boolean
  /**
   * Isvenuelocation
   * @default false
   */
  isVenueLocation?: boolean
  /** Label */
  label?: string | null
  /** Latitude */
  latitude: number | string
  /** Longitude */
  longitude: number | string
  /**
   * Postalcode
   * @minLength 5
   * @maxLength 5
   */
  postalCode: string
  /**
   * Street
   * @minLength 1
   * @maxLength 200
   */
  street: string
}

/** LocationOnlyOnVenueBodyModel */
export interface LocationOnlyOnVenueBodyModel {
  /** Isvenuelocation */
  isVenueLocation: boolean
}

/** LocationResponseModel */
export interface LocationResponseModel {
  /** Banid */
  banId?: string | null
  /** City */
  city: string
  /** Departmentcode */
  departmentCode?: string | null
  /** Id */
  id: number
  /** Inseecode */
  inseeCode?: string | null
  /** Ismanualedition */
  isManualEdition: boolean
  /** Isvenuelocation */
  isVenueLocation: boolean
  /** Label */
  label?: string | null
  /** Latitude */
  latitude: number
  /** Longitude */
  longitude: number
  /** Postalcode */
  postalCode: string
  /** Street */
  street?: string | null
}

/** LoginUserBodyModel */
export interface LoginUserBodyModel {
  /**
   * Captchatoken
   * @default null
   */
  captchaToken?: string | null
  /** Identifier */
  identifier: string
  /** Password */
  password: string
}

/** ManagedVenue */
export interface ManagedVenue {
  /** Bankaccountid */
  bankAccountId: number | null
  /** Commonname */
  commonName: string
  /** Haspricingpoint */
  hasPricingPoint: boolean
  /** Id */
  id: number
  /** Name */
  name: string
  /** Siret */
  siret: string | null
}

/** MentalDisabilityModel */
export interface MentalDisabilityModel {
  /**
   * Trainedpersonnel
   * @default "Non renseigné"
   */
  trainedPersonnel?: string
}

/** MinimalPostOfferBodyModel */
export interface MinimalPostOfferBodyModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant: boolean
  /** Description */
  description?: string | null
  /** Durationminutes */
  durationMinutes?: number | null
  /** Extradata */
  extraData?: object | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant: boolean
  /** Motordisabilitycompliant */
  motorDisabilityCompliant: boolean
  /** Name */
  name: string
  /** Subcategoryid */
  subcategoryId: string
  /** Venueid */
  venueId: number
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant: boolean
}

/** MotorDisabilityModel */
export interface MotorDisabilityModel {
  /**
   * Entrance
   * @default "Non renseigné"
   */
  entrance?: string
  /**
   * Exterior
   * @default "Non renseigné"
   */
  exterior?: string
  /**
   * Facilities
   * @default "Non renseigné"
   */
  facilities?: string
  /**
   * Parking
   * @default "Non renseigné"
   */
  parking?: string
}

/** MusicTypeResponse */
export interface MusicTypeResponse {
  /** Canbeevent */
  canBeEvent: boolean
  /** Gtl Id */
  gtl_id: string
  /** Label */
  label: string
}

/** NationalProgramModel */
export interface NationalProgramModel {
  /**
   * Id
   * National program id
   * @example 1223456
   */
  id: number
  /**
   * Name
   * National program name
   * @example "Collège au cinéma"
   */
  name: string
}

/** NationalProgramResponseModel */
export interface NationalProgramResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** NewPasswordBodyModel */
export interface NewPasswordBodyModel {
  /**
   * Newpassword
   * @minLength 1
   */
  newPassword: string
  /**
   * Token
   * @minLength 1
   */
  token: string
}

/** OfferDomain */
export interface OfferDomain {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** OfferImage */
export interface OfferImage {
  /** Credit */
  credit?: string
  /** Url */
  url: string
}

/** OfferImageV2 */
export interface OfferImageV2 {
  /**
   * Credit
   * @default null
   */
  credit?: string | null
  /** Url */
  url: string
}

/** OfferOpeningHoursSchema */
export interface OfferOpeningHoursSchema {
  openingHours: WeekdayOpeningHoursTimespans
}

/** OffererEligibilityResponseModel */
export interface OffererEligibilityResponseModel {
  /** Hasadageid */
  hasAdageId?: boolean | null
  /** Hasdsapplication */
  hasDsApplication?: boolean | null
  /** Isonboarded */
  isOnboarded?: boolean | null
  /** Offererid */
  offererId: number
}

/** OffererStatsDataModel */
export interface OffererStatsDataModel {
  /** Dailyviews */
  dailyViews: OffererViewsModel[]
  /** Topoffers */
  topOffers: TopOffersResponseData[]
  /** Totalviewslast30Days */
  totalViewsLast30Days: number
}

/** OffererViewsModel */
export interface OffererViewsModel {
  /**
   * Eventdate
   * @format date
   */
  eventDate: string
  /** Numberofviews */
  numberOfViews: number
}

/** PatchAllOffersActiveStatusBodyModel */
export interface PatchAllOffersActiveStatusBodyModel {
  /** Categoryid */
  categoryId?: string | null
  /** Creationmode */
  creationMode?: string | null
  /** Isactive */
  isActive: boolean
  /** Nameorisbn */
  nameOrIsbn?: string | null
  /** Offereraddressid */
  offererAddressId?: number | null
  /** Offererid */
  offererId?: number | null
  /**
   * Periodbeginningdate
   * @format date
   */
  periodBeginningDate?: string | null
  /**
   * Periodendingdate
   * @format date
   */
  periodEndingDate?: string | null
  /** Status */
  status?: string | null
  /** Venueid */
  venueId?: number | null
}

/** PatchCollectiveOfferActiveStatusBodyModel */
export interface PatchCollectiveOfferActiveStatusBodyModel {
  /** Ids */
  ids: number[]
  /** Isactive */
  isActive: boolean
}

/** PatchCollectiveOfferArchiveBodyModel */
export interface PatchCollectiveOfferArchiveBodyModel {
  /** Ids */
  ids: number[]
}

/** PatchCollectiveOfferBodyModel */
export interface PatchCollectiveOfferBodyModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** Bookingemails */
  bookingEmails?: string[] | null
  /**
   * Contactemail
   * @format email
   */
  contactEmail?: string | null
  /** Contactphone */
  contactPhone?: string | null
  /** Description */
  description?: string | null
  /** Domains */
  domains?: number[] | null
  /** Durationminutes */
  durationMinutes?: number | null
  formats?: EacFormat[] | null
  /** Interventionarea */
  interventionArea?: string[] | null
  /** CollectiveOfferLocationModel */
  location?: CollectiveOfferLocationModel | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name?: string | null
  /** Nationalprogramid */
  nationalProgramId?: number | null
  students?: StudentLevels[] | null
  /** Venueid */
  venueId?: number | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** PatchCollectiveOfferEducationalInstitution */
export interface PatchCollectiveOfferEducationalInstitution {
  /** Educationalinstitutionid */
  educationalInstitutionId: number
  /** Teacheremail */
  teacherEmail?: string | null
}

/** PatchCollectiveOfferTemplateBodyModel */
export interface PatchCollectiveOfferTemplateBodyModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /** Bookingemails */
  bookingEmails?: string[] | null
  /**
   * Contactemail
   * @format email
   */
  contactEmail?: string | null
  contactForm?: OfferContactFormEnum | null
  /** Contactphone */
  contactPhone?: string | null
  /** Contacturl */
  contactUrl?: string | null
  /** DateRangeModel */
  dates?: DateRangeModel | null
  /** Description */
  description?: string | null
  /** Domains */
  domains?: number[] | null
  /** Durationminutes */
  durationMinutes?: number | null
  formats?: EacFormat[] | null
  /** Interventionarea */
  interventionArea?: string[] | null
  /** CollectiveOfferLocationModel */
  location?: CollectiveOfferLocationModel | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name?: string | null
  /** Nationalprogramid */
  nationalProgramId?: number | null
  /**
   * Pricedetail
   * @maxLength 1000
   */
  priceDetail?: string | null
  students?: StudentLevels[] | null
  /** Venueid */
  venueId?: number | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
}

/** PatchOfferActiveStatusBodyModel */
export interface PatchOfferActiveStatusBodyModel {
  /** Ids */
  ids: number[]
  /** Isactive */
  isActive: boolean
}

/** PatchOfferBodyModel */
export interface PatchOfferBodyModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  /**
   * Bookingalloweddatetime
   * @format date-time
   */
  bookingAllowedDatetime?: string | null
  /**
   * Bookingcontact
   * @format email
   */
  bookingContact?: string | null
  /**
   * Bookingemail
   * @format email
   */
  bookingEmail?: string | null
  /** Description */
  description?: string | null
  /** Durationminutes */
  durationMinutes?: number | null
  /**
   * Externalticketofficeurl
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  externalTicketOfficeUrl?: string | null
  /** Extradata */
  extraData?: any
  /** Isduo */
  isDuo?: boolean | null
  /** Isnational */
  isNational?: boolean | null
  /** Location */
  location?: LocationBodyModel | LocationOnlyOnVenueBodyModel | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name?: string | null
  /** Publicationdatetime */
  publicationDatetime?: string | 'now' | null
  /** Shouldsendmail */
  shouldSendMail?: boolean | null
  /** Subcategoryid */
  subcategoryId?: string | null
  /**
   * Url
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  url?: string | null
  /**
   * Videourl
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  videoUrl?: string | null
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /** Withdrawaldelay */
  withdrawalDelay?: number | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
  withdrawalType?: WithdrawalTypeEnum | null
}

/** PatchOfferPublishBodyModel */
export interface PatchOfferPublishBodyModel {
  /**
   * Bookingalloweddatetime
   * @format date-time
   */
  bookingAllowedDatetime?: string | null
  /** Id */
  id: number
  /**
   * Publicationdatetime
   * @format date-time
   */
  publicationDatetime?: string | null
}

/** PostCollectiveOfferBodyModel */
export interface PostCollectiveOfferBodyModel {
  /**
   * Audiodisabilitycompliant
   * @default false
   */
  audioDisabilityCompliant?: boolean
  /** Bookingemails */
  bookingEmails: string[]
  /**
   * Contactemail
   * @format email
   */
  contactEmail?: string | null
  /** Contactphone */
  contactPhone?: string | null
  /** Description */
  description: string
  /** Domains */
  domains: number[]
  /** Durationminutes */
  durationMinutes?: number | null
  formats: EacFormat[]
  /** Interventionarea */
  interventionArea?: string[] | null
  location: CollectiveOfferLocationModel
  /**
   * Mentaldisabilitycompliant
   * @default false
   */
  mentalDisabilityCompliant?: boolean
  /**
   * Motordisabilitycompliant
   * @default false
   */
  motorDisabilityCompliant?: boolean
  /** Name */
  name: string
  /** Nationalprogramid */
  nationalProgramId?: number | null
  students: StudentLevels[]
  /** Templateid */
  templateId?: number | null
  /** Venueid */
  venueId: number
  /**
   * Visualdisabilitycompliant
   * @default false
   */
  visualDisabilityCompliant?: boolean
}

/** PostCollectiveOfferTemplateBodyModel */
export interface PostCollectiveOfferTemplateBodyModel {
  /**
   * Audiodisabilitycompliant
   * @default false
   */
  audioDisabilityCompliant?: boolean
  /** Bookingemails */
  bookingEmails: string[]
  /**
   * Contactemail
   * @format email
   */
  contactEmail?: string | null
  contactForm?: OfferContactFormEnum | null
  /** Contactphone */
  contactPhone?: string | null
  /**
   * Contacturl
   * @format uri
   * @minLength 1
   * @maxLength 65536
   */
  contactUrl?: string | null
  /** DateRangeOnCreateModel */
  dates?: DateRangeOnCreateModel | null
  /** Description */
  description: string
  /** Domains */
  domains: number[]
  /** Durationminutes */
  durationMinutes?: number | null
  formats: EacFormat[]
  /** Interventionarea */
  interventionArea?: string[] | null
  location: CollectiveOfferLocationModel
  /**
   * Mentaldisabilitycompliant
   * @default false
   */
  mentalDisabilityCompliant?: boolean
  /**
   * Motordisabilitycompliant
   * @default false
   */
  motorDisabilityCompliant?: boolean
  /** Name */
  name: string
  /** Nationalprogramid */
  nationalProgramId?: number | null
  /**
   * Pricedetail
   * @maxLength 1000
   */
  priceDetail?: string | null
  students: StudentLevels[]
  /** Templateid */
  templateId?: number | null
  /** Venueid */
  venueId: number
  /**
   * Visualdisabilitycompliant
   * @default false
   */
  visualDisabilityCompliant?: boolean
}

/** PostOfferBodyModel */
export interface PostOfferBodyModel {
  /** Address */
  address?: LocationBodyModel | LocationOnlyOnVenueBodyModel | null
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant: boolean
  /**
   * Bookingcontact
   * @format email
   */
  bookingContact?: string | null
  /**
   * Bookingemail
   * @format email
   */
  bookingEmail?: string | null
  /** Description */
  description?: string | null
  /** Durationminutes */
  durationMinutes?: number | null
  /**
   * Externalticketofficeurl
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  externalTicketOfficeUrl?: string | null
  /** Extradata */
  extraData?: object | null
  /** Isduo */
  isDuo?: boolean | null
  /** Isnational */
  isNational?: boolean | null
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant: boolean
  /** Motordisabilitycompliant */
  motorDisabilityCompliant: boolean
  /** Name */
  name: string
  /** Productid */
  productId?: number | null
  /** Subcategoryid */
  subcategoryId: string
  /**
   * Url
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  url?: string | null
  /** Venueid */
  venueId: number
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant: boolean
  /** Withdrawaldelay */
  withdrawalDelay?: number | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
  withdrawalType?: WithdrawalTypeEnum | null
}

/** PostOffererResponseModel */
export interface PostOffererResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
  /** Siren */
  siren: string
}

/** PostVenueProviderBody */
export interface PostVenueProviderBody {
  /**
   * Isactive
   * @default null
   */
  isActive?: boolean | null
  /**
   * Isduo
   * @default null
   */
  isDuo?: boolean | null
  /**
   * Price
   * @default null
   */
  price?: number | null
  /** Providerid */
  providerId: number
  /**
   * Quantity
   * @default null
   */
  quantity?: number | null
  /** Venueid */
  venueId: number
  /**
   * Venueidatofferprovider
   * @default null
   */
  venueIdAtOfferProvider?: string | null
}

/** PriceCategoryBody */
export interface PriceCategoryBody {
  /**
   * Pricecategories
   * @maxItems 50
   */
  priceCategories: (CreatePriceCategoryModel | EditPriceCategoryModel)[]
}

/** PriceCategoryResponseModel */
export interface PriceCategoryResponseModel {
  /** Id */
  id: number
  /** Label */
  label: string
  /** Price */
  price: number
}

/** ProAnonymizationEligibilityResponseModel */
export interface ProAnonymizationEligibilityResponseModel {
  /** Hassuspendedofferer */
  hasSuspendedOfferer: boolean
  /** Isonlypro */
  isOnlyPro: boolean
  /** Issoleuserwithongoingactivities */
  isSoleUserWithOngoingActivities: boolean
}

/** ProUserCreationBodyV2Model */
export interface ProUserCreationBodyV2Model {
  /** Contactok */
  contactOk: boolean
  /**
   * Email
   * @format email
   */
  email: string
  /** Firstname */
  firstName: string
  /** Lastname */
  lastName: string
  /** Password */
  password: string
  /**
   * Phonenumber
   * @default null
   */
  phoneNumber?: string | null
  /** Token */
  token: string
}

/** ProviderResponse */
export interface ProviderResponse {
  /** Enabledforpro */
  enabledForPro: boolean
  /** Hasoffererprovider */
  hasOffererProvider: boolean
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Name */
  name: string
}

/** ReimbursementCsvByInvoicesModel */
export interface ReimbursementCsvByInvoicesModel {
  /**
   * Invoicesreferences
   * @maxItems 75
   * @uniqueItems true
   */
  invoicesReferences: string[]
}

/** ResetPasswordBodyModel */
export interface ResetPasswordBodyModel {
  /**
   * Email
   * @format email
   */
  email: string
  /**
   * Token
   * @minLength 1
   */
  token: string
}

/** SaveNewOnboardingDataQueryModel */
export interface SaveNewOnboardingDataQueryModel {
  /** Activity */
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic | null
  address: LocationBodyModel
  /**
   * Createvenuewithoutsiret
   * @default false
   */
  createVenueWithoutSiret?: boolean
  /**
   * Culturaldomains
   * @minItems 1
   */
  culturalDomains?: string[] | null
  /** Isopentopublic */
  isOpenToPublic: boolean
  /** Phonenumber */
  phoneNumber?: string | null
  /** Publicname */
  publicName?: string | null
  /** Siret */
  siret: string
  /** An enumeration. */
  target: Target
  /** Token */
  token: string
  /** Venuetypecode */
  venueTypeCode?: string | null
  /** Webpresence */
  webPresence: string
}

/** SharedCurrentUserResponseModel */
export interface SharedCurrentUserResponseModel {
  /**
   * Activity
   * @default null
   */
  activity?: string | null
  /**
   * Address
   * @default null
   */
  address?: string | null
  /**
   * City
   * @default null
   */
  city?: string | null
  /** @default null */
  civility?: GenderEnum | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /**
   * Dateofbirth
   * @default null
   */
  dateOfBirth?: string | null
  /**
   * Departementcode
   * @default null
   */
  departementCode?: string | null
  /** Email */
  email: string
  /**
   * Externalids
   * @default null
   */
  externalIds?: Record<string, any> | null
  /**
   * Firstname
   * @default null
   */
  firstName?: string | null
  /**
   * Hasseenprotutorials
   * @default null
   */
  hasSeenProTutorials?: boolean | null
  /**
   * Hasuserofferer
   * @default null
   */
  hasUserOfferer?: boolean | null
  /** Id */
  id: number
  /**
   * Idpiecenumber
   * @default null
   */
  idPieceNumber?: string | null
  /** Isemailvalidated */
  isEmailValidated: boolean
  /**
   * Isimpersonated
   * @default false
   */
  isImpersonated?: boolean
  /**
   * Lastconnectiondate
   * @default null
   */
  lastConnectionDate?: string | null
  /**
   * Lastname
   * @default null
   */
  lastName?: string | null
  /**
   * Needstofillculturalsurvey
   * @default null
   */
  needsToFillCulturalSurvey?: boolean | null
  /**
   * Notificationsubscriptions
   * @default null
   */
  notificationSubscriptions?: Record<string, any> | null
  /**
   * Phonenumber
   * @default null
   */
  phoneNumber?: string | null
  /** @default null */
  phoneValidationStatus?: PhoneValidationStatusType | null
  /**
   * Postalcode
   * @default null
   */
  postalCode?: string | null
  /** Roles */
  roles: UserRole[]
}

/** SharedLoginUserResponseModel */
export interface SharedLoginUserResponseModel {
  /**
   * Activity
   * @default null
   */
  activity?: string | null
  /**
   * Address
   * @default null
   */
  address?: string | null
  /**
   * City
   * @default null
   */
  city?: string | null
  /** @default null */
  civility?: GenderEnum | null
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /**
   * Dateofbirth
   * @default null
   */
  dateOfBirth?: string | null
  /**
   * Departementcode
   * @default null
   */
  departementCode?: string | null
  /** Email */
  email: string
  /**
   * Firstname
   * @default null
   */
  firstName?: string | null
  /**
   * Hasseenprotutorials
   * @default null
   */
  hasSeenProTutorials?: boolean | null
  /**
   * Hasuserofferer
   * @default null
   */
  hasUserOfferer?: boolean | null
  /** Id */
  id: number
  /** Isemailvalidated */
  isEmailValidated: boolean
  /**
   * Lastconnectiondate
   * @default null
   */
  lastConnectionDate?: string | null
  /**
   * Lastname
   * @default null
   */
  lastName?: string | null
  /**
   * Needstofillculturalsurvey
   * @default null
   */
  needsToFillCulturalSurvey?: boolean | null
  /**
   * Phonenumber
   * @default null
   */
  phoneNumber?: string | null
  /**
   * Postalcode
   * @default null
   */
  postalCode?: string | null
  /** Roles */
  roles: UserRole[]
}

/** ShortHighlightResponseModel */
export interface ShortHighlightResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** StatisticsModel */
export interface StatisticsModel {
  /** Incomebyyear */
  incomeByYear: Record<string, AggregatedRevenueModel | Record<string, null>>
}

/** StatisticsQueryModel */
export interface StatisticsQueryModel {
  /**
   * Venueids
   * @default []
   */
  venueIds?: number[]
}

/** StockStatsResponseModel */
export interface StockStatsResponseModel {
  /**
   * Neweststock
   * @format date-time
   */
  newestStock?: string | null
  /**
   * Oldeststock
   * @format date-time
   */
  oldestStock?: string | null
  /** Remainingquantity */
  remainingQuantity?: number | null
  /** Stockcount */
  stockCount?: number | null
}

/** StocksQueryModel */
export interface StocksQueryModel {
  /**
   * Date
   * @format date
   */
  date?: string | null
  /** @default "BEGINNING_DATETIME" */
  order_by?: StocksOrderedBy
  /**
   * Order By Desc
   * @default false
   */
  order_by_desc?: boolean
  /**
   * Page
   * @min 1
   * @default 1
   */
  page?: number
  /** Price Category Id */
  price_category_id?: number | null
  /**
   * Stocks Limit Per Page
   * @default 20
   */
  stocks_limit_per_page?: number
  /**
   * Time
   * @format time
   */
  time?: string | null
}

/** StructureDataBodyModel */
export interface StructureDataBodyModel {
  /** Apecode */
  apeCode?: string | null
  /** Isdiffusible */
  isDiffusible: boolean
  /** LocationModel */
  location?: LocationModel | null
  /** Name */
  name?: string | null
  /** Siren */
  siren?: string | null
  /** Siret */
  siret: string
}

/** SubcategoryResponseModel */
export interface SubcategoryResponseModel {
  /** Applabel */
  appLabel: string
  /** Canbeduo */
  canBeDuo: boolean
  /** Canbewithdrawable */
  canBeWithdrawable: boolean
  /** Canexpire */
  canExpire: boolean
  /** Canhaveopeninghours */
  canHaveOpeningHours: boolean
  /** Categoryid */
  categoryId: string
  /** Conditionalfields */
  conditionalFields: string[]
  /** Id */
  id: string
  /** Isdigitaldeposit */
  isDigitalDeposit: boolean
  /** Isevent */
  isEvent: boolean
  /** Isphysicaldeposit */
  isPhysicalDeposit: boolean
  /** Isselectable */
  isSelectable: boolean
  /** Onlineofflineplatform */
  onlineOfflinePlatform: string
  /** Prolabel */
  proLabel: string
  /** Reimbursementrule */
  reimbursementRule: string
}

/** SubmitReviewRequestModel */
export interface SubmitReviewRequestModel {
  /** Location */
  location: string
  /** Offererid */
  offererId: number
  /** Pagetitle */
  pageTitle: string
  /** Usercomment */
  userComment: string
  /** Usersatisfaction */
  userSatisfaction: string
}

/** ThingStockUpsertBodyModel */
export interface ThingStockUpsertBodyModel {
  /**
   * Activationcodes
   * @default null
   */
  activationCodes?: string[] | null
  /**
   * Activationcodesexpirationdatetime
   * @default null
   */
  activationCodesExpirationDatetime?: string | null
  /**
   * Bookinglimitdatetime
   * @default null
   */
  bookingLimitDatetime?: string | null
  /**
   * Id
   * @default null
   */
  id?: number | null
  /** Offerid */
  offerId: number
  /** Price */
  price: number
  /**
   * Quantity
   * @default null
   */
  quantity?: number | null
}

/** ThingStocksBulkUpsertBodyModel */
export interface ThingStocksBulkUpsertBodyModel {
  /** Stocks */
  stocks: ThingStockUpsertBodyModel[]
}

/** TopOffersResponseData */
export interface TopOffersResponseData {
  image?: OfferImage
  /** Isheadlineoffer */
  isHeadlineOffer: boolean
  /** Numberofviews */
  numberOfViews: number
  /** Offerid */
  offerId: number
  /** Offername */
  offerName: string
}

/** TotalRevenue */
export interface TotalRevenue {
  /** Collective */
  collective: number
  /** Individual */
  individual: number
  /** Total */
  total: number
}

/** UserEmailValidationResponseModel */
export interface UserEmailValidationResponseModel {
  /**
   * Newemail
   * @default null
   */
  newEmail?: string | null
}

/** UserHasBookingResponse */
export interface UserHasBookingResponse {
  /** Hasbookings */
  hasBookings: boolean
}

/** UserIdentityBodyModel */
export interface UserIdentityBodyModel {
  /** Firstname */
  firstName: string
  /** Lastname */
  lastName: string
}

/** UserIdentityResponseModel */
export interface UserIdentityResponseModel {
  /** Firstname */
  firstName: string
  /** Lastname */
  lastName: string
}

/** UserPhoneBodyModel */
export interface UserPhoneBodyModel {
  /** Phonenumber */
  phoneNumber: string
}

/** UserPhoneResponseModel */
export interface UserPhoneResponseModel {
  /** Phonenumber */
  phoneNumber: string
}

/** UserResetEmailBodyModel */
export interface UserResetEmailBodyModel {
  /**
   * Email
   * @format email
   */
  email: string
  /** Password */
  password: string
}

/**
 * ValidationError
 * Model of a validation error response.
 */
export type ValidationError = ValidationErrorElement[]

/**
 * ValidationErrorElement
 * Model of a validation error response element.
 */
export interface ValidationErrorElement {
  /** Error context */
  ctx?: object
  /** Missing field name */
  loc: string[]
  /** Error message */
  msg: string
  /** Error type */
  type: string
}

/** VenueContactModel */
export interface VenueContactModel {
  /**
   * Email
   * @format email
   */
  email?: string | null
  /** Phonenumber */
  phoneNumber?: string | null
  /** Socialmedias */
  socialMedias?: Record<string, string>
  /** Website */
  website?: string | null
}

/** VenueLabelListResponseModel */
export type VenueLabelListResponseModel = VenueLabelResponseModel[]

/** VenueLabelResponseModel */
export interface VenueLabelResponseModel {
  /** Id */
  id: number
  /** Label */
  label: string
}

/** VenueListItemLiteResponseModel */
export interface VenueListItemLiteResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** VenueListItemResponseModel */
export interface VenueListItemResponseModel {
  /** Audiodisabilitycompliant */
  audioDisabilityCompliant?: boolean | null
  bankAccountStatus?: SimplifiedBankAccountStatus | null
  /** Bookingemail */
  bookingEmail?: string | null
  /** ExternalAccessibilityDataModel */
  externalAccessibilityData?: ExternalAccessibilityDataModel | null
  /** Hascreatedoffer */
  hasCreatedOffer: boolean
  /** Hasnonfreeoffers */
  hasNonFreeOffers: boolean
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Iscaledonian */
  isCaledonian: boolean
  /** Ispermanent */
  isPermanent: boolean
  /** Isvalidated */
  isValidated: boolean
  /** Isvirtual */
  isVirtual: boolean
  /** LocationResponseModel */
  location?: LocationResponseModel | null
  /** Managingoffererid */
  managingOffererId: number
  /** Mentaldisabilitycompliant */
  mentalDisabilityCompliant?: boolean | null
  /** Motordisabilitycompliant */
  motorDisabilityCompliant?: boolean | null
  /** Name */
  name: string
  /** Offerername */
  offererName: string
  /** Publicname */
  publicName?: string | null
  /** Siret */
  siret?: string | null
  /** An enumeration. */
  venueTypeCode: VenueTypeCode
  /** Visualdisabilitycompliant */
  visualDisabilityCompliant?: boolean | null
  /** Withdrawaldetails */
  withdrawalDetails?: string | null
}

/** VenueListQueryModel */
export interface VenueListQueryModel {
  /** Activeofferersonly */
  activeOfferersOnly?: boolean | null
  /** Offererid */
  offererId?: number | null
  /** Validated */
  validated?: boolean | null
}

/** VenueOfOffererFromSiretResponseModel */
export interface VenueOfOffererFromSiretResponseModel {
  /** Id */
  id: number
  /** Ispermanent */
  isPermanent: boolean
  /** Name */
  name: string
  /** Publicname */
  publicName?: string | null
  /** Siret */
  siret?: string | null
}

/** VenueProviderResponse */
export interface VenueProviderResponse {
  /**
   * Datecreated
   * @format date-time
   */
  dateCreated: string
  /** Id */
  id: number
  /** Isactive */
  isActive: boolean
  /** Isduo */
  isDuo: boolean | null
  /** Isfromallocineprovider */
  isFromAllocineProvider: boolean
  /** Lastsyncdate */
  lastSyncDate: string | null
  /**
   * Price
   * @default null
   */
  price?: number | null
  provider: ProviderResponse
  /**
   * Quantity
   * @default null
   */
  quantity?: number | null
  /** Venueid */
  venueId: number
  /** Venueidatofferprovider */
  venueIdAtOfferProvider: string | null
}

/** VenueTypeListResponseModel */
export type VenueTypeListResponseModel = VenueTypeResponseModelV2[]

/** VenueTypeResponseModel */
export interface VenueTypeResponseModel {
  /** Label */
  label: string
  /** Value */
  value: string
}

/** VenueTypeResponseModelV2 */
export interface VenueTypeResponseModelV2 {
  /** Label */
  label: string
  /** Value */
  value: string
}

/** VenuesEducationalStatusResponseModel */
export interface VenuesEducationalStatusResponseModel {
  /** Id */
  id: number
  /** Name */
  name: string
}

/** VenuesEducationalStatusesResponseModel */
export interface VenuesEducationalStatusesResponseModel {
  /** Statuses */
  statuses: VenuesEducationalStatusResponseModel[]
}

/** VideoData */
export interface VideoData {
  /** Videoduration */
  videoDuration?: number | null
  /** Videoexternalid */
  videoExternalId?: string | null
  /** Videothumbnailurl */
  videoThumbnailUrl?: string | null
  /** Videotitle */
  videoTitle?: string | null
  /**
   * Videourl
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  videoUrl?: string | null
}

/** VideoMetatdataQueryModel */
export interface VideoMetatdataQueryModel {
  /**
   * Videourl
   * @format uri
   * @minLength 1
   * @maxLength 2083
   */
  videoUrl: string
}

/** VisualDisabilityModel */
export interface VisualDisabilityModel {
  /**
   * Audiodescription
   * @default ["Non renseigné"]
   */
  audioDescription?: string[]
  /**
   * Soundbeacon
   * @default "Non renseigné"
   */
  soundBeacon?: string
}

/** WeekdayOpeningHoursTimespans */
export interface WeekdayOpeningHoursTimespans {
  /**
   * Friday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  FRIDAY?: string[][] | null
  /**
   * Monday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  MONDAY?: string[][] | null
  /**
   * Saturday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  SATURDAY?: string[][] | null
  /**
   * Sunday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  SUNDAY?: string[][] | null
  /**
   * Thursday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  THURSDAY?: string[][] | null
  /**
   * Tuesday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  TUESDAY?: string[][] | null
  /**
   * Wednesday
   * @maxItems 2
   * @minItems 1
   * @uniqueItems true
   */
  WEDNESDAY?: string[][] | null
}
