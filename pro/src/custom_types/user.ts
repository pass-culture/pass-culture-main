export type UserInfo = {
  firstName: string
  lastName: string
  email: string
  phoneNumber: string
}

enum PhoneValidationStatus {
  BLOCKED_TOO_MANY_CODE_SENDINGS = 'blocked-too-many-code-sendings',
  BLOCKED_TOO_MANY_CODE_VERIFICATION_TRIES = 'blocked-too-many-code-verification-tries',
  VALIDATED = 'validated',
}

enum UserRole {
  ADMIN = 'ADMIN',
  BENEFICIARY = 'BENEFICIARY',
  PRO = 'PRO',
  JOUVE = 'JOUVE',
  UNDERAGE_BENEFICIARY = 'UNDERAGE_BENEFICIARY',
}

export type User = {
  activity?: string
  address?: string
  city?: string
  civility?: string
  dateCreated: Date
  dateOfBirth?: Date
  departementCode?: string
  email: string
  externalIds?: Record<string, string>
  firstName?: string
  hasCompletedIdCheck?: boolean
  hasPhysicalVenues?: boolean
  hasSeenProTutorials?: boolean
  id: string
  idPieceNumber?: string
  isAdmin: boolean
  isEmailValidated: boolean
  lastConnectionDate?: Date
  lastName?: string
  needsToFillCulturalSurvey?: boolean
  notificationSubscriptions?: Record<string, boolean>
  phoneNumber?: string
  phoneValidationStatus?: PhoneValidationStatus
  postalCode?: string
  publicName?: string
  roles: UserRole[]
}
