import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import { Chip } from '@mui/material'

import { FraudCheckStatus } from '../types'

type Props = {
  active?: boolean
  fraudCheckStatus: FraudCheckStatus
}

export const FraudCheckStatusBadge = ({
  fraudCheckStatus: checkHistoryStatus,
}: Props) => {
  const chipLabel = checkHistoryStatus.toUpperCase()
  const fontSize = '1rem'

  switch (checkHistoryStatus) {
    case FraudCheckStatus.OK:
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
    case FraudCheckStatus.KO:
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
