import {
  BankAccountResponseModel,
  DMSApplicationForEAC,
  GetVenueResponseModel,
  LegalStatusResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import { VenueBannerMetaProps } from 'components/VenueForm/ImageUploaderVenue/ImageUploaderVenue'
import { AccessibiltyFormValues } from 'core/shared'

export type IndividualOfferVenueItem = {
  id: number
  managingOffererId: number
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
  accessibility: AccessibiltyFormValues
  bookingEmail?: string | null
  hasMissingReimbursementPoint: boolean
  hasCreatedOffer: boolean
  venueType: string
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

export interface Venue extends GetVenueResponseModel {
  accessibility: AccessibiltyFormValues
  address: string
  banId: string
  bannerMeta: VenueBannerMetaProps | null | undefined
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
  isPermanent: boolean
  isVenueVirtual: boolean
  latitude: number
  longitude: number
  mail: string
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
  collectiveDmsApplication: DMSApplicationForEAC | null
  bankAccount: BankAccountResponseModel | null
}

export type Providers = {
  id: number
  isActive: boolean
  name: string
  hasOffererProvider: boolean
}
