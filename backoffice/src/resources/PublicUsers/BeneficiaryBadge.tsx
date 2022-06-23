import { Chip } from '@mui/material'

import { PublicUserRolesEnum } from '../Interfaces/UserSearchInterface'

type Props = {
  role: PublicUserRolesEnum
}

export const BeneficiaryBadge = ({ role }: Props) => {
  let label
  switch (role) {
    case PublicUserRolesEnum.beneficiary:
      label = 'Pass 18'
      break
    case PublicUserRolesEnum.underageBeneficiary:
      label = 'Pass 15-17'
      break
    default:
      return null
  }
  return (
    <Chip
      color={'info'}
      label={label}
      style={{
        fontSize: '0.95rem',
      }}
    />
  )
}
