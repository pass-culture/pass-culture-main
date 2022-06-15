import { Identifier, RaRecord } from 'react-admin'

export enum PublicUserRolesEnum {
  beneficiary = 'BENEFICIARY',
  underageBeneficiary = 'UNDERAGE_BENEFICIARY',
}

export interface UserApiInterface extends RaRecord {
  id: Identifier
  firstName: string
  lastName: string
  dateOfBirth: string
  email: string
  roles: [PublicUserRolesEnum]
  phoneNumber: string
  isActive: Boolean
}

export interface UserSearchInterface {
  accounts: UserApiInterface[]
}
