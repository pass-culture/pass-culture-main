import { Chip } from '@mui/material'

import { ValidationStatus } from '../../../TypesFromApi'
import { ProTypeEnum } from '../types'

type Props = {
  status: ValidationStatus
  resourceType: ProTypeEnum
}

export const ValidationStatusBadge = ({ status, resourceType }: Props) => {
  let label = ''
  let color:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning'

  switch (status) {
    case ValidationStatus.NEW:
      label = resourceType == ProTypeEnum.offerer ? 'Nouvelle' : 'Nouveau'
      color = 'info'
      break
    case ValidationStatus.PENDING:
      label = 'En attente'
      color = 'warning'
      break
    case ValidationStatus.REJECTED:
      label = resourceType == ProTypeEnum.offerer ? 'Rejetée' : 'Rejeté'
      color = 'error'
      break
    case ValidationStatus.VALIDATED:
      label = resourceType == ProTypeEnum.offerer ? 'Validée' : 'Validé'
      color = 'success'
      break
    default:
      label = 'Non disponible'
      color = 'default'
      break
  }
  return (
    <Chip
      color={color}
      label={label}
      style={{
        fontSize: '0.95rem',
      }}
    />
  )
}
