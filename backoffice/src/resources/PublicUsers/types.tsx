import { Identifier, RaRecord } from 'react-admin'

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
  id: string
  eligibility?: 'UNDERAGE' | 'AGE18'
  reason: string
  review: 'OK' | 'KO' | 'REDIRECTED_TO_DMS'
}

export enum SubscriptionItemStatus {
  KO = 'ko',
  OK = 'ko',
  NOT_APPLICABLE = 'not-applicable',
  VOID = 'void',
}

export interface CheckHistoryTechnicalDetails {
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

export interface CheckHistory {
  type: string
  thirdPartyId: string
  dateCreated: Date
  status: 'ok' | 'void' | 'not-applicable' | 'ko'
  reason?: string
  reasonCodes?: string
  technicalDetails?: CheckHistoryTechnicalDetails
  sourceId?: string
}

export interface UserCredit {
  dateCreated: Date
  initialCredit: number
  remainingCredit: number
  remainingDigitalCredit: number
}

export interface CheckHistories {
  histories: CheckHistory[]
}
