import {
  DMSApplicationForEAC,
  GetVenueDomainResponseModel,
  GetVenueManagingOffererResponseModel,
  GetVenueResponseModel,
  LegalStatusResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import { IAccessibiltyFormValues } from 'core/shared'
import { IVenueBannerMetaProps } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'

export type TOfferIndividualVenue = {
  id: string
  nonHumanizedId: number
  managingOffererId: string
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
  accessibility: IAccessibiltyFormValues
  bookingEmail?: string | null
  hasMissingReimbursementPoint: boolean
  hasCreatedOffer: boolean
}

export type VenueCollectiveInformation = Pick<
  GetVenueResponseModel,
  | 'collectiveDescription'
  | 'collectiveDomains'
  | 'collectiveEmail'
  | 'collectiveInterventionArea'
  | 'collectiveLegalStatus'
  | 'collectiveNetwork'
  | 'collectivePhone'
  | 'collectiveStudents'
  | 'collectiveWebsite'
  | 'collectiveSubCategoryId'
>

export interface IVenue {
  collectiveDomains: Array<GetVenueDomainResponseModel>
  dateCreated: string
  fieldsUpdated: Array<string>
  isVirtual: boolean
  managingOffererId: string
  accessibility: IAccessibiltyFormValues
  address: string
  bannerMeta: IVenueBannerMetaProps | null | undefined
  bannerUrl: string
  city: string
  hasPendingBankInformationApplication: boolean | null
  demarchesSimplifieesApplicationId: string | null
  comment: string
  contact: {
    email: string | null
    phoneNumber: string | null
    webSite: string | null
  }
  description: string
  departmentCode: string
  dmsToken: string
  id: string
  isPermanent: boolean
  isVenueVirtual: boolean
  latitude: number
  longitude: number
  mail: string
  name: string
  managingOfferer: GetVenueManagingOffererResponseModel
  nonHumanizedId: number
  pricingPoint: {
    id: number
    siret: string
    venueName: string
  } | null
  postalCode: string
  publicName: string
  siret: string
  venueType: string
  venueLabel: string | null
  reimbursementPointId: number | null
  withdrawalDetails: string
  collectiveAccessInformation: string
  collectiveDescription: string
  collectiveEmail: string
  collectiveInterventionArea: Array<string>
  collectiveLegalStatus: LegalStatusResponseModel | null
  collectiveNetwork: Array<string>
  collectivePhone: string
  collectiveStudents: Array<StudentLevels>
  collectiveWebsite: string
  adageInscriptionDate: string | null
  hasAdageId: boolean
  collectiveDmsApplication: DMSApplicationForEAC | null
}

export type IProviders = {
  enabledForPro: boolean
  id: string
  isActive: boolean
  name: string
  hasOffererProvider: boolean
}
