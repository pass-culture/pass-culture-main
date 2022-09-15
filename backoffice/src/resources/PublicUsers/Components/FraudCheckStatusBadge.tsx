import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import SecurityIcon from '@mui/icons-material/Security'
import { Chip } from '@mui/material'

import { FraudCheckStatus } from '../../../TypesFromApi'

type Props = {
  fraudCheckStatus: FraudCheckStatus
}

export const FraudCheckStatusBadge = ({ fraudCheckStatus }: Props) => {
  const chipLabel = fraudCheckStatus.toUpperCase()
  const fontSize = '1rem'

  switch (fraudCheckStatus) {
    case FraudCheckStatus.Ok:
      return (
        <Chip
          color={'success'}
          label={chipLabel}
          icon={<CheckCircleOutlineIcon />}
          style={{
            fontSize: fontSize,
          }}
        />
      )
    case FraudCheckStatus.Ko:
      return (
        <Chip
          color={'error'}
          label={chipLabel}
          icon={<ErrorOutlineIcon />}
          style={{
            fontSize: fontSize,
          }}
        />
      )
    case FraudCheckStatus.Suspiscious:
      return (
        <Chip
          color={'warning'}
          label={chipLabel}
          icon={<SecurityIcon />}
          style={{
            fontSize: fontSize,
          }}
        />
      )
    default:
      return (
        <Chip
          color={'warning'}
          label={chipLabel}
          icon={<ErrorOutlineIcon />}
          style={{
            fontSize: fontSize,
          }}
        />
      )
  }
}
