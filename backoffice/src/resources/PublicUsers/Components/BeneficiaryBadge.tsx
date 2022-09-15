import { Chip } from '@mui/material'

import { UserRole } from '../../../TypesFromApi'

type Props = {
  role: UserRole
}

export const BeneficiaryBadge = ({ role }: Props) => {
  let label
  switch (role) {
    case UserRole.BENEFICIARY:
      label = 'Pass 18'
      break
    case UserRole.UNDERAGEBENEFICIARY:
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
