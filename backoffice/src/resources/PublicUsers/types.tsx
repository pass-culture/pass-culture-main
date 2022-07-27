import { Identifier, RaRecord } from 'react-admin'

export enum PublicUserRolesEnum {
  beneficiary = 'BENEFICIARY',
  underageBeneficiary = 'UNDERAGE_BENEFICIARY',
}

export interface UserApiResponse extends RaRecord {
  id: Identifier
  firstName: string
  lastName: string
  dateOfBirth: string
  email: string
  roles: [PublicUserRolesEnum]
  phoneNumber: string
  isActive: boolean
}

export interface UserSearchResponse {
  accounts: UserApiResponse[]
}
export interface UserBaseInfo extends RaRecord {
  id: Identifier
  lastName: string
  firstName: string
  email: string
  phoneNumer?: string
  dateOfBirth: Date
  address?: string
  postalCode?: string
  city?: string
}

export interface UserManualReview {
  id: number
  eligibility?: 'UNDERAGE' | 'AGE18'
  reason: string
  review: 'OK' | 'KO' | 'REDIRECTED_TO_DMS'
}

export enum SubscriptionItemStatus {
  KO = 'ko',
  OK = 'ok',
  NOT_APPLICABLE = 'not-applicable',
  NOT_ENABLED = 'not-enabled',
  VOID = 'void',
}
export enum SubscriptionItemType {
  EMAIL_VALIDATION = 'email-validation',
  PHONE_VALIDATION = 'phone-validation',
  PROFILE_COMPLETION = 'profile-completion',
  IDENTITY_CHECK = 'identity-check',
  HONOR_STATEMENT = 'honor-statement',
}

export interface EligibilitySubscriptionItem {
  role: PublicUserRolesEnum
  items: SubscriptionItem[]
}

export interface SubscriptionItem {
  type: SubscriptionItemType
  status: SubscriptionItemStatus
}

export interface EligibilityFraudCheck {
  role: PublicUserRolesEnum
  items: FraudCheck[]
}
export interface FraudCheckTechnicalDetails {
  score?: string
  gender?: string
  status?: string
  comment?: string
  lastName: string
  supported?: boolean
  birthDate: Date
  firstName: string
  marriedName?: string
  documentType?: null
  expiryDateScore?: Date
  identificationId?: string
  idDocumentNumber?: string
  identificationUrl?: string
  registrationDateTime: Date
}

export interface FraudCheck {
  type: string
  thirdPartyId: string
  dateCreated: Date
  status: 'ok' | 'void' | 'not-applicable' | 'ko' | 'not-enabled'
  reason?: string
  reasonCodes?: string
  technicalDetails?: FraudCheckTechnicalDetails
  sourceId?: string
}
