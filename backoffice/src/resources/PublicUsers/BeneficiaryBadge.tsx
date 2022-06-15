import { Chip } from '@mui/material'
import { PublicUserRolesEnum } from '../Interfaces/UserSearchInterface'

export const BeneficiaryBadge = (role: PublicUserRolesEnum) => {
  let element
  switch (role) {
    case PublicUserRolesEnum.beneficiary:
      element = <Chip color={'secondary'} label={'Pass 18'} />
      break
    case PublicUserRolesEnum.underageBeneficiary:
      element = <Chip color={'secondary'} label={'Pass 15-17'} />
      break
    default:
      break
  }
  return <>{element}</>
}
