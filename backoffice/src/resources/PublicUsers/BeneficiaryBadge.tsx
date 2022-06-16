import { Chip } from '@mui/material'

import { PublicUserRolesEnum } from '../Interfaces/UserSearchInterface'

type Props = {
  role: PublicUserRolesEnum
}

export const BeneficiaryBadge = ({ role }: Props) => {
  switch (role) {
    case PublicUserRolesEnum.beneficiary:
      return <Chip color={'secondary'} label={'Pass 18'} />
    case PublicUserRolesEnum.underageBeneficiary:
      return <Chip color={'secondary'} label={'Pass 15-17'} />
    default:
      return null
  }
}
