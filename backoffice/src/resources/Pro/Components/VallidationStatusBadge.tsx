import { Chip } from '@mui/material'

import { ValidationStatus } from '../../../TypesFromApi'

type Props = {
  status: ValidationStatus
}

export const ValidationStatusBadge = ({ status }: Props) => {
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
      label = 'Nouveau'
      color = 'info'
      break
    case ValidationStatus.PENDING:
      label = 'En attente'
      color = 'warning'
      break
    case ValidationStatus.REJECTED:
      label = 'Rejeté'
      color = 'error'
      break
    case ValidationStatus.VALIDATED:
      label = 'Validé'
      color = 'success'
      break
    default:
      label = 'Non disponible'
      color = 'default'
      break
  }
  return <Chip color={color} label={label} />
}
