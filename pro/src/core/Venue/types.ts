import {
  GetVenueManagingOffererResponseModel,
  GetVenueDomainResponseModel,
  GetVenueResponseModel,
  LegalStatusResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import { IAccessibiltyFormValues } from 'core/shared'

export type TOfferIndividualVenue = {
  id: string
  managingOffererId: string
  name: string
  isVirtual: boolean
  withdrawalDetails: string | null
  accessibility: IAccessibiltyFormValues
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
>

export interface IVenue {
  collectiveDomains: Array<GetVenueDomainResponseModel>
  dateCreated: string
  fieldsUpdated: Array<string>
  isValidated: boolean
  isVirtual: boolean
  managingOffererId: string
  accessibility: IAccessibiltyFormValues
  address: string
  bannerMeta: IVenueBannerMetaProps | null | undefined
  bannerUrl: string
  city: string
  comment: string
  contact: {
    email: string
    phoneNumber: string
    webSite: string
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
  venueLabel: string
  reimbursementPointId: number
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
}

export type IProviders = {
  enabledForPro: boolean
  id: string
  isActive: boolean
  name: string
}

export type IVenueProviderApi = {
  id: string
  idAtProviders: string | null
  dateModifiedAtLastProvider: string | null
  isActive: boolean
  isFromAllocineProvider: boolean
  lastProviderId: string | null
  lastSyncDate: string | null
  nOffers: number
  providerId: string
  venueId: string
  venueIdAtOfferProvider: string
  provider: any
  quantity?: number
  isDuo: boolean | null
  price: number
}
