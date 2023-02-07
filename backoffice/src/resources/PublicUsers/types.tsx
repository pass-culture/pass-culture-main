import { Identifier, RaRecord } from 'react-admin'

export enum PublicUserRolesEnum {
  beneficiary = 'BENEFICIARY',
  underageBeneficiary = 'UNDERAGE_BENEFICIARY',
}

export enum PermissionsEnum {
  managePermissions = 'MANAGE_PERMISSIONS',
  readPublicAccount = 'READ_PUBLIC_ACCOUNT',
  reviewPublicAccount = 'REVIEW_SUSPEND_USER',
  managePublicAccount = 'MANAGE_PUBLIC_ACCOUNT',
  searchPublicAccount = 'SEARCH_PUBLIC_ACCOUNT',
  searchProAccount = 'SEARCH_PRO_ACCOUNT',
  readProEntity = 'READ_PRO_ENTITY',
  manageProEntity = 'MANAGE_PRO_ENTITY',
  validateOfferer = 'VALIDATE_OFFERER',
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

export interface FraudCheckTechnicalDetails {
  // a garder en attendant la specification API
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
